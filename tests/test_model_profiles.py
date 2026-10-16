import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import setup_local_tutor as installer


class ModelProfileTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.data = Path(self.temporary.name)
        self.patch = patch.object(installer, 'DATA', self.data)
        self.patch.start()
        for profile, (repo, revision, _, _) in installer.MODEL_PROFILES.items():
            directory = self.data / 'models' / profile
            directory.mkdir(parents=True)
            # These are inert fixtures; no model executable is run by this test.
            (directory / 'weights.gguf').write_bytes(profile.encode())
            (directory / 'mmproj-F16.gguf').write_bytes((profile + '-projector').encode())
            (directory / 'LICENSE-model').write_text('Apache License Version 2.0')
            (directory / 'MODEL-CARD.md').write_text('Quantizer fixture')
            (directory / 'BASE-MODEL-CARD.md').write_text('Base fixture')
            (directory / 'model.json').write_text(json.dumps({
                'repository': repo, 'revision': revision, 'filename': 'weights.gguf',
                'sha256': installer.sha256(directory / 'weights.gguf'),
                'projector': 'mmproj-F16.gguf', 'projector_sha256': installer.sha256(directory / 'mmproj-F16.gguf'),
                'license_sha256': installer.sha256(directory / 'LICENSE-model'),
            }))

    def tearDown(self):
        self.patch.stop()
        self.temporary.cleanup()

    def test_cached_profile_switch_uses_its_own_projector_without_network(self):
        with patch.object(installer.urllib.request, 'urlopen', side_effect=AssertionError('Unexpected network call')):
            for profile in ['qwen35-4b', 'qwen35-9b', 'qwen35-4b']:
                model = installer.setup_model(profile)
                active = json.loads((self.data / 'models/model.json').read_text())
                self.assertEqual(model.read_bytes(), profile.encode())
                projector = self.data / 'models' / active['projector']
                self.assertEqual(projector.read_bytes(), (profile + '-projector').encode())
                self.assertTrue(str(projector.relative_to(self.data / 'models')).startswith(profile + '/'))

    def test_damaged_candidate_does_not_replace_the_active_profile(self):
        installer.setup_model('qwen35-4b')
        before = (self.data / 'models/model.json').read_bytes()
        (self.data / 'models/qwen35-9b/mmproj-F16.gguf').write_bytes(b'damaged')
        with patch.object(installer.urllib.request, 'urlopen', side_effect=OSError('Offline during repair')):
            with self.assertRaises(OSError):
                installer.setup_model('qwen35-9b')
        self.assertEqual((self.data / 'models/model.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
