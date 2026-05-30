import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web.app import app  # noqa: E402


class WebAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_sample_endpoint(self):
        response = self.client.get("/api/sample")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("prompt", data)
        self.assertIn("outline", data)

    def test_outline_then_generate_then_download(self):
        outline_response = self.client.post(
            "/api/outline",
            data={"prompt": "请生成人工智能课堂汇报大纲"},
            content_type="multipart/form-data",
        )
        self.assertEqual(outline_response.status_code, 200)
        outline_data = outline_response.get_json()
        self.assertTrue(outline_data["session_id"])
        self.assertTrue(outline_data["outline"])

        generate_response = self.client.post(
            "/api/generate",
            data=json.dumps(
                {
                    "session_id": outline_data["session_id"],
                    "outline": outline_data["outline"],
                    "template_name": "",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(generate_response.status_code, 200)
        generate_data = generate_response.get_json()
        self.assertIn("download_url", generate_data)

        download_response = self.client.get(generate_data["download_url"])
        self.assertEqual(download_response.status_code, 200)
        self.assertGreater(len(download_response.data), 0)
        self.assertEqual(download_response.data[:2], b"PK")


if __name__ == "__main__":
    unittest.main()
