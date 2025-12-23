import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        request_data = {
            messages: [msg.to_dict() for msg in messages]
        }

        response = requests.post(self._endpoint, headers=self.headers, json=request_data)
        print(response.json())

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        content = response.json().get['choices'][0]['message']['content']
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=self.headers, json=request_data) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")

                async for line in response.content:
                    if line.startswith(b"data: ") and b"[DONE]" not in line:
                        content_chunk = json.loads(line[6:])['choices'][0]['delta'].get('content', '')
                        if content_chunk:
                            contents.append(content_chunk)
                            print(content_chunk, end='', flush=True)
        print()
        return Message(role=Role.AI, content=''.join(contents))
