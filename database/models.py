"""
SQLAlchemy ORM models for the Interview Prep Bot.
"""
import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def _now():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    target_role = Column(String(120), nullable=False)
    experience = Column(String(50), nullable=False)
    skills = Column(Text, default="")
    preferred_technology = Column(String(80), default="Python")
    created_at = Column(DateTime, default=_now)

    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    performance_records = relationship(
        "Performance", back_populates="user", cascade="all, delete-orphan"
    )


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_type = Column(String(50), nullable=False)
    technology = Column(String(80), nullable=False)
    difficulty = Column(String(30), nullable=False)
    total_questions = Column(Integer, default=0)
    final_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=_now)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="in_progress")  # in_progress | completed | abandoned

    user = relationship("User", back_populates="interviews")
    questions = relationship(
        "Question", back_populates="interview", cascade="all, delete-orphan"
    )
    performance_records = relationship(
        "Performance", back_populates="interview", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String(80), default="General")
    difficulty = Column(String(30), default="Medium")
    question_type = Column(String(50), default="Technical")
    order_number = Column(Integer, default=0)

    interview = relationship("Interview", back_populates="questions")
    answer = relationship(
        "Answer", back_populates="question", uselist=False, cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Text, default="")
    score = Column(Integer, default=0)
    technical_accuracy = Column(Integer, default=0)
    relevance = Column(Integer, default=0)
    completeness = Column(Integer, default=0)
    clarity = Column(Integer, default=0)
    feedback = Column(Text, default="")
    strengths = Column(Text, default="")       # stored as "|"-joined string
    weaknesses = Column(Text, default="")       # stored as "|"-joined string
    missing_concepts = Column(Text, default="")  # stored as "|"-joined string
    ideal_answer = Column(Text, default="")
    created_at = Column(DateTime, default=_now)

    question = relationship("Question", back_populates="answer")


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    topic = Column(String(80), nullable=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="performance_records")
    interview = relationship("Interview", back_populates="performance_records")
