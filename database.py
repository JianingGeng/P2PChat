# database.py

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import bcrypt

engine = create_engine("sqlite:///mydatabase.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    ip_address = Column(String)  # 添加这行来存储用户的IP地址
    password_hash = Column(String)
    is_online = Column(Boolean, default=False)  # 添加这个字段来追踪用户是否在线
    port = Column(Integer)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


def set_user_online(username, online=True):
    """设置用户的在线状态"""
    session = scoped_session(Session)()
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.is_online = online
        session.commit()
    session.remove()


def get_online_users():
    """获取当前在线的所有用户"""
    session = scoped_session(Session)()
    online_users = session.query(User).filter_by(is_online=True).all()
    session.remove()
    return [user.username for user in online_users]


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    sender_username = Column(String, ForeignKey("users.username"))
    recipient_username = Column(String, ForeignKey("users.username"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)  # 添加这个字段来追踪消息是否已读


def store_message(sender, recipient, content):
    """存储消息到数据库"""
    session = Session()
    message = Message(
        sender_username=sender, recipient_username=recipient, content=content
    )
    session.add(message)
    session.commit()
    session.close()


def get_unread_messages(username):
    """从数据库中检索未读消息"""
    session = scoped_session(Session)()
    unread_messages = (
        session.query(Message)
        .filter_by(recipient_username=username, is_read=False)
        .all()
    )
    session.remove()
    return unread_messages


def mark_message_as_read(message_id):
    """将消息标记为已读"""
    session = scoped_session(Session)()
    message = session.query(Message).filter_by(id=message_id).first()
    if message:
        message.is_read = True
        session.commit()
    session.remove()


# 在数据库中创建表
# 这一行代码是在所有模型类定义之后添加的
Base.metadata.create_all(engine)

# 创建会话工厂
Session = sessionmaker(bind=engine)
