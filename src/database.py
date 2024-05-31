import os
import uuid
from random import shuffle
from typing import Optional, List, Tuple

from sqlalchemy import create_engine, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, Session
from sqlalchemy.dialects.postgresql import UUID


engine = create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['DB_SERVER']}/{os.environ['POSTGRES_DB']}")


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = "question"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    context_word: Mapped[str]
    context_sentence: Mapped[str]
    definitions: Mapped[List["Definition"]] = relationship(back_populates="question")


class Definition(Base):
    __tablename__ = "definition_response"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generator_id: Mapped[UUID] = mapped_column(ForeignKey("definition_generator.id"))
    generator: Mapped["DefinitionGenerator"] = relationship(back_populates="definitions")
    question_id: Mapped[str] = mapped_column(ForeignKey("question.id"))
    question: Mapped["Question"] = relationship(back_populates="definitions")
    text: Mapped[str]


class DefinitionGenerator(Base):
    __tablename__ = "definition_generator"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str]
    name: Mapped[str]
    desc: Mapped[Optional[str]]
    example_prompt: Mapped[Optional[str]]
    question_prompt: Mapped[Optional[str]]
    system_prompt: Mapped[Optional[str]]
    definitions: Mapped[List["Definition"]] = relationship(back_populates="generator")


class UserResponse(Base):
    __tablename__ = "user_response"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    question: Mapped[str] = mapped_column(ForeignKey("question.id"))
    left: Mapped[UUID] = mapped_column(ForeignKey("definition_response.id"))
    right: Mapped[UUID] = mapped_column(ForeignKey("definition_response.id"))
    winner: Mapped[int]


class QuestionError(Base):
    __tablename__ = "question_error"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    question: Mapped[str] = mapped_column(ForeignKey("question.id"))


class User(Base):
    __tablename__ = "user"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ipaddress: Mapped[str]


def random_question() -> Tuple[Question, Definition, Definition, DefinitionGenerator, DefinitionGenerator]:
    with Session(engine) as sess:
        question = sess.query(Question).order_by(func.random()).first()
        definitions = list(question.definitions)
        shuffle(definitions)
        definitions = definitions[:2]
        generators = [d.generator for d in definitions]
    return question, *definitions, *generators


def submit_response(question, left, right, winner, session_id):
    with Session(engine) as sess:
        user_session = sess.get(User, session_id)
        if not user_session:
            user_session = User(id=session_id, ipaddress="")
            sess.add(user_session)
            sess.flush()
        sess.add(UserResponse(session=session_id, question=question, left=left, right=right, winner=winner))
        sess.commit()


def submit_error(question, session_id):
    with Session(engine) as sess:
        user_session = sess.get(User, session_id)
        if not user_session:
            user_session = User(id=session_id, ipaddress="")
            sess.add(user_session)
            sess.flush()
        sess.add(QuestionError(session=session_id, question=question))
        sess.commit()


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
