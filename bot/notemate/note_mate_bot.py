# encoding:utf-8

import time

from bot.bot import Bot
from bot.session_manager import SessionManager
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf

from pydantic import BaseModel, Field
import requests


user_session = dict()

class UserInput(BaseModel):
    """Basic user input for the agent."""

    message: str = Field(
        description="User input to the agent.",
        examples=["What is the weather in Tokyo?"],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )

# OpenAI对话模型API (可用)
class NoteMateBot(Bot):
    def __init__(self):
        super().__init__()
        self.api_key = conf().get("note_mate_api_key")
        self.api_base = conf().get("note_mate_api_base")
        self.timeout = conf().get("note_mate_timeout")
        self.headers = {}
        self.headers["Authorization"] = f"Bearer {self.api_key}"


    def reply(self, query, context=None):
        # acquire reply content
        if context and context.type:
            if context.type == ContextType.TEXT:
                logger.info("[NOTE_MATE] query={}".format(query))
                session_id = context["session_id"]
                reply = None
                
                result = self.reply_text(query, session_id)
                total_tokens, completion_tokens, reply_content = (
                    result["total_tokens"],
                    result["completion_tokens"],
                    result["content"],
                )
                logger.debug(
                    "[NOTE_MATE] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format( query, session_id, reply_content, completion_tokens)
                )

                if total_tokens == 0:
                    reply = Reply(ReplyType.ERROR, reply_content)
                else:
                    reply = Reply(ReplyType.TEXT, reply_content)
                return reply
            elif context.type == ContextType.IMAGE_CREATE:
                ok, retstring = self.create_img(query, 0)
                reply = None
                if ok:
                    reply = Reply(ReplyType.IMAGE_URL, retstring)
                else:
                    reply = Reply(ReplyType.ERROR, retstring)
                return reply

    def reply_text(self, message, session_id, retry_count=0):
        try:
            request = UserInput(message=message)
            request.thread_id = session_id

            response = requests.post(
                f"{self.api_base}/invoke",
                json=request.model_dump(),
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info("[NOTE_MATE] response={}".format(response.content))
            total_tokens = response_data['original']['data']['response_metadata']["token_usage"]["total_tokens"]
            completion_tokens = response_data['original']['data']['response_metadata']["token_usage"]["completion_tokens"]
            res_content = response_data["content"]
            logger.info("[NOTE_MATE] reply={}".format(res_content))
            return {
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "content": res_content,
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            
            if need_retry:
                logger.warn("[NOTE_MATE] 第{}次重试".format(retry_count + 1))
                return self.reply_text(message, session_id, retry_count + 1)
            else:
                return result
