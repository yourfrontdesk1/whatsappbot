import requests


class WhatsApp360Dialog:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://waba.360dialog.io/v1"
        self.headers = {
            "D360-API-KEY": api_key,
            "Content-Type": "application/json"
        }

    def send_message(self, to: str, text: str) -> bool:
        """Send text message via 360dialog"""

        url = f"{self.base_url}/messages"

        payload = {
            "to": to,
            "type": "text",
            "text": {
                "body": text
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return True

        except Exception as e:
            print(f"360dialog API error: {e}")
            return False

    def send_template(self, to: str, template_name: str, language: str = "en") -> bool:
        """Send template message"""

        url = f"{self.base_url}/messages"

        payload = {
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language
                }
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return True

        except Exception as e:
            print(f"Template send error: {e}")
            return False
