from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    定义聊天消息的数据结构
    """
    role: str = Field(description="消息发送者角色")
    content: str = Field(description="消息内容")


class Role:
    AI = 'assistant'
    USER = 'user'
    SYSTEM = 'system'


def ai_message(text: str) -> Message:
    """
    创建AI角色消息
    :param text:
    :return:
    """
    return Message(role=Role.AI, content=text)


def user_message(text: str) -> Message:
    """
    创建用户角色消息
    :param text:
    :return:
    """
    return Message(role=Role.USER, content=text)


def system_message(text: str) -> Message:
    """
    创建系统角色消息
    :param text:
    :return:
    """
    return Message(role=Role.SYSTEM, content=text)
