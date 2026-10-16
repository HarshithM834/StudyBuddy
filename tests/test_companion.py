import base64
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image

from server import app as application
from server.follow import match_slide
from test_api import test_pdf


class FollowTests(unittest.TestCase):
    def test_unique_slide_and_ambiguous_two_slide_view(self):
        first = 'Wireless stations sleep while access points buffer unicast traffic until delivery notification.'
        second = 'Hamming parity checks detect and correct a single flipped data bit using overlapping groups.'
        pages = [(1, first), (2, second)]
        self.assertEqual(match_slide('Canvas Home Courses ' + first, pages)['page'], 1)
        self.assertEqual(match_slide(second, pages)['page'], 2)
        self.assertEqual(match_slide(first + second, pages)['status'], 'ambiguous')
        self.assertIsNone(match_slide('Canvas Home Courses Calendar Assignments', pages)['page'])

    def test_duplicate_pages_and_shared_footer_do_not_guess(self):
        content = 'Network identifiers distinguish the service set name from the unique access point address.'
        self.assertIsNone(match_slide(content, [(1, content), (2, content)])['page'])
        self.assertIsNone(match_slide('CYSE wireless communication 2026', [(1, content)])['page'])

    def test_contained_slide_text_does_not_hide_the_longer_slide(self):
        short = 'Wireless clients sleep while access points buffer unicast packets.'
        extra = 'Traffic indication maps announce buffered delivery during the next beacon interval.'
        self.assertEqual(match_slide(short + extra, [(1, short), (2, short + extra)])['page'], 2)

    def test_two_differently_sized_visible_slides_remain_ambiguous(self):
        first = 'Parity overlapping checks detect flipped data bits.'
        second = ('Wireless sleeping stations rely on infrastructure access points which buffer incoming unicast packets '
                  'until scheduled beacon delivery announcements wake associated clients and allow power conservation.')
        self.assertIsNone(match_slide(first + second, [(1, first), (2, second)])['page'])


class CompanionAPITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.previous = application.DATA_DIR
        application.DATA_DIR = Path(self.temporary.name)
        application.initialize()
        self.client = TestClient(application.app)
        image = io.BytesIO()
        Image.new('RGB', (160, 100), '#eeeeee').save(image, format='JPEG')
        self.body = {'context_id': 'a' * 64, 'application': 'Safari', 'title': 'Canvas · Lecture',
                     'text': 'A private visible-screen phrase', 'image': 'data:image/jpeg;base64,' + base64.b64encode(image.getvalue()).decode(),
                     'message': 'Explain the visible concept', 'intent': 'explain'}

    def tearDown(self):
        self.client.close()
        application.DATA_DIR = self.previous
        self.temporary.cleanup()

    def test_screen_turn_is_local_bounded_and_persists_only_completed_history(self):
        answer = application.TutorResponse(answer='A visible explanation.', citations=[9], visual=None)
        with patch.object(application, 'ask_local', new=AsyncMock(return_value=answer)) as model:
            response = self.client.post('/api/companion/chat', json=self.body)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['messages'][-1]['citations'], [])
        instructions, context, images, prior, _ = model.call_args.args
        self.assertIn('not a recording, audio, video transcript', instructions)
        self.assertIn(self.body['text'], context)
        self.assertTrue(images[0]['image_url'].startswith('data:image/jpeg;base64,'))
        self.assertEqual(prior, [])
        saved = self.client.get('/api/companion/contexts/' + 'a' * 64).json()
        self.assertEqual(saved, response.json())
        self.assertEqual(self.client.get('/api/companion/contexts/' + 'b' * 64).json()['messages'], [])
        # No screenshot/OCR file, or raw OCR/database column, is retained.
        with application.database() as db:
            row = dict(db.execute('SELECT * FROM screen_work').fetchone())
        self.assertNotIn(self.body['text'], str(row))
        self.assertNotIn(self.body['image'], str(row))
        self.assertEqual(list((application.DATA_DIR / 'images').iterdir()), [])

    def test_failed_turn_remote_url_and_invalid_images_save_nothing(self):
        with patch.object(application, 'ask_local', new=AsyncMock(side_effect=HTTPException(504, 'Timed out'))):
            self.assertEqual(self.client.post('/api/companion/chat', json=self.body).status_code, 504)
        with patch.dict('os.environ', {'STUDYBUDDY_LOCAL_URL': 'https://example.com'}), patch.object(application, 'ask_local', new=AsyncMock()) as model:
            self.assertEqual(self.client.post('/api/companion/chat', json=self.body).status_code, 503)
            model.assert_not_awaited()
        for image in ['https://example.com/screen.jpg', 'data:image/jpeg;base64,broken']:
            self.assertEqual(self.client.post('/api/companion/chat', json={**self.body, 'image': image}).status_code, 422)
        self.assertEqual(self.client.get('/api/companion/contexts/' + 'a' * 64).json()['messages'], [])

    def test_following_uses_chosen_course_and_never_saves_window_text(self):
        document = self.client.post('/api/documents', files={'file': ('Lecture.pdf', test_pdf(), 'application/pdf')}).json()['id']
        path = f'/api/documents/{document}/follow'
        phrase = 'Wireless stations sleep while access points buffer unicast traffic until delivery notification.'
        with application.database() as db:
            db.execute('UPDATE pages SET text=? WHERE document_id=? AND number=1', (phrase, document))
        self.assertEqual(self.client.post(path + '/match', json={'text': phrase}).status_code, 409)
        with patch.object(application, 'page_text', side_effect=lambda _doc, _page, text: text):
            self.assertEqual(self.client.post(path + '/prepare').status_code, 200)
        self.assertEqual(self.client.post(path + '/match', json={'text': phrase}).json()['page'], 1)
        self.assertIsNone(self.client.post(path + '/match', json={'text': 'YouTube new unrelated video'}).json()['page'])
        self.assertEqual(self.client.get(f'/api/documents/{document}/pages/1/work').json()['messages'], [])
