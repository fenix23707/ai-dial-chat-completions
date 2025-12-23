import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool, client) -> None:

    conversation = Conversation()
    system_prompt = input("Enter system prompt (or press Enter to use default): ").strip() or DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))

    while True:
        user_message = input("Enter your message('exit' to stop): ").strip()
        if user_message.lower() == 'exit':
            return

        conversation.add_message(Message(role=Role.USER, content=user_message))
        if stream:
            response = await client.stream_completion(conversation.get_messages())
        else:
            response = client.get_completion(conversation.get_messages())
        conversation.add_message(response)

    #TODO:
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response

# asyncio.run(start(False, DialClient(deployment_name="gpt-4")))
# asyncio.run(start(True, DialClient(deployment_name="gpt-4")))

# asyncio.run(start(False, CustomDialClient(deployment_name="gpt-4")))
asyncio.run(start(True, CustomDialClient(deployment_name="gpt-4")))
