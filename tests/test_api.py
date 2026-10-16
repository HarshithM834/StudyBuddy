import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pypdfium2 as pdfium
import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient

from server import app as application


def test_pdf(pages=2):
    output = io.BytesIO()
    with pdfium.PdfDocument.new() as document:
        for _ in range(pages):
            page = document.new_page(400, 300)
            page.close()
        document.save(output)
    return output.getvalue()


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original = application.DATA_DIR
        application.DATA_DIR = Path(self.directory.name)
        application.initialize()
        self.client = TestClient(application.app)
        self.pdf = test_pdf()
        response = self.client.post('/api/documents', files={'file': ('lecture.pdf', self.pdf, 'application/pdf')})
        self.assertEqual(response.status_code, 201)
        self.document = response.json()['id']
        self.base = f'/api/documents/{self.document}/pages'

    def tearDown(self):
        self.client.close()
        application.DATA_DIR = self.original
        self.directory.cleanup()

    def test_import_is_idempotent_and_pdf_renders(self):
        second = self.client.post('/api/documents', files={'file': ('copy.pdf', self.pdf, 'application/pdf')})
        self.assertEqual(second.json()['id'], self.document)
        self.assertEqual(len(self.client.get('/api/documents').json()), 1)
        response = self.client.get(f'{self.base}/1/image?width=300')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'\x89PNG'))
        original = self.client.get(f'/api/documents/{self.document}/file')
        self.assertEqual(original.content, self.pdf)

    def test_notes_and_annotations_are_isolated_and_survive_reads(self):
        mark = {'id': 'pin-1', 'kind': 'pin', 'x': .3, 'y': .4, 'width': 0, 'height': 0, 'text': 'A question'}
        self.assertEqual(self.client.put(f'{self.base}/1/marks', json={'marks': [mark]}).status_code, 200)
        self.assertEqual(self.client.put(f'{self.base}/1/notes', json={'text': 'My own explanation'}).status_code, 200)
        first = self.client.get(f'{self.base}/1/work').json()
        self.assertEqual(first['notes'], 'My own explanation')
        self.assertEqual(first['marks'], [mark])
        second = self.client.get(f'{self.base}/2/work').json()
        self.assertEqual(second, {'notes': '', 'marks': [], 'messages': []})
        page_list = self.client.get(f'/api/documents/{self.document}').json()['pages']
        self.assertIs(page_list[0]['has_work'], True)
        self.assertIs(page_list[1]['has_work'], False)

    def test_rejects_invalid_pdf_and_invalid_slide(self):
        response = self.client.post('/api/documents', files={'file': ('bad.pdf', b'not a PDF', 'application/pdf')})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get(f'{self.base}/999/work').status_code, 404)
        self.assertEqual(self.client.get(f'{self.base}/0/image').status_code, 404)
        self.assertEqual(self.client.get(f'{self.base}/1/image?width=99999').status_code, 422)

    def test_rejects_out_of_bounds_annotations(self):
        mark = {'id': 'x', 'kind': 'highlight', 'x': -1, 'y': .2, 'width': .1, 'height': .1}
        self.assertEqual(self.client.put(f'{self.base}/1/marks', json={'marks': [mark]}).status_code, 422)

    def test_chat_persists_source_links_and_visuals(self):
        result = application.TutorResponse(answer='Here is one useful step.', citations=[1, 2, 999], visual=application.Diagram(title='A relationship', nodes=[application.DiagramNode(id='a', label='First'), application.DiagramNode(id='b', label='Second')], edges=[application.DiagramEdge(source='a', target='b', label='leads to'), application.DiagramEdge(source='a', target='missing', label='bad')]))
        with patch.dict(os.environ, {'STUDYBUDDY_PROVIDER': 'local'}), patch.object(application, 'ask_local', new=AsyncMock(return_value=result)) as local:
            response = self.client.post(f'{self.base}/1/chat', json={'message': 'Show this visually', 'intent': 'visualize'})
            self.assertEqual(response.status_code, 200, response.text)
            messages = response.json()['messages']
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]['role'], 'user')
            self.assertEqual(messages[1]['citations'], [1, 2])
            self.assertEqual(len(messages[1]['visual']['edges']), 1)
            self.assertEqual(self.client.get(f'{self.base}/1/work').json()['messages'], messages)
            self.assertEqual(self.client.get(f'{self.base}/2/work').json()['messages'], [])
            local.assert_awaited_once()

    def test_unavailable_local_tutor_does_not_record_a_fake_answer(self):
        with patch.dict(os.environ, {'STUDYBUDDY_PROVIDER': 'local'}), patch.object(application, 'ask_local', new=AsyncMock(side_effect=HTTPException(503, 'Local tutor offline'))):
            response = self.client.post(f'{self.base}/1/chat', json={'message': 'Explain this'})
            self.assertEqual(response.status_code, 503)
            self.assertEqual(self.client.get(f'{self.base}/1/work').json()['messages'], [])


    def test_tutor_rejects_remote_endpoints_before_inference(self):
        with patch.dict(os.environ, {'STUDYBUDDY_LOCAL_URL': 'https://api.example.com'}), patch.object(application, 'ask_local', new=AsyncMock()) as local:
            response = self.client.post(f'{self.base}/1/chat', json={'message': 'Explain this'})
            self.assertEqual(response.status_code, 503)
            self.assertIn('local model server', response.json()['detail'])
            local.assert_not_awaited()
            # An inference configuration error must not hide the PDF library.
            health = self.client.get('/api/health')
            self.assertEqual(health.status_code, 200)
            self.assertFalse(health.json()['tutor_configured'])
            self.assertEqual(len(self.client.get('/api/documents').json()), 1)

    def test_legacy_paid_provider_setting_cannot_select_a_remote_provider(self):
        answer = application.TutorResponse(answer='A local answer.', citations=[1], visual=None)
        with patch.dict(os.environ, {'STUDYBUDDY_PROVIDER': 'openai'}), patch.object(application, 'ask_local', new=AsyncMock(return_value=answer)) as local:
            response = self.client.post(f'{self.base}/1/chat', json={'message': 'Explain this'})
            self.assertEqual(response.status_code, 200)
            local.assert_awaited_once()

    def test_incomplete_model_reply_does_not_change_saved_work(self):
        self.client.put(f'{self.base}/1/notes', json={'text': 'Keep my own notes'})
        original_client = httpx.AsyncClient
        for content, finish_reason in [('{"answer":"Partial","citations":[],"visual":null}', 'length'),
                                       ('{"answer":" ","citations":[],"visual":null}', 'stop')]:
            with self.subTest(finish_reason=finish_reason):
                def respond(request):
                    self.assertEqual(request.url.host, '127.0.0.1')
                    return httpx.Response(200, json={'choices': [{'finish_reason': finish_reason, 'message': {'content': content}}]})
                def local_client(**kwargs):
                    return original_client(**kwargs, transport=httpx.MockTransport(respond))
                with patch.object(application, 'build_context', return_value=('A lecture excerpt', [], {1})), patch.object(application.httpx, 'AsyncClient', side_effect=local_client):
                    response = self.client.post(f'{self.base}/1/chat', json={'message': 'Explain this'})
                self.assertEqual(response.status_code, 502)
                work = self.client.get(f'{self.base}/1/work').json()
                self.assertEqual(work['notes'], 'Keep my own notes')
                self.assertEqual(work['messages'], [])


if __name__ == '__main__':
    unittest.main()
