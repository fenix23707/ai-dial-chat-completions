from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.client = Dial(base_url=DIAL_ENDPOINT, api_key=API_KEY)
        self.async_client = AsyncDial(base_url=DIAL_ENDPOINT, api_key=API_KEY)

    def get_completion(self, messages: list[Message]) -> Message:
        completion = self.client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[msg.to_dict() for msg in messages]
        )
        if not completion.choices:
            raise Exception("No choices in response found")

        content = completion.choices[0].message.content
        print(content)
        return Message(role=Role.AI, content=content)


    async def stream_completion(self, messages: list[Message]) -> Message:
        completion = await self.async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=[msg.to_dict() for msg in messages]
        )
        contents = []
        async for chunk in completion:
            content_chunk = chunk.choices[0].delta.content
            if content_chunk:
                print(content_chunk, end='', flush=True)
                contents.append(content_chunk)
        print()
        return Message(role=Role.AI, content=''.join(contents))