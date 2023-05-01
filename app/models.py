from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, Integer, Numeric, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.database import Base
from typing import List


association_table = Table(
    "user_loans",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("loan_id", ForeignKey("loans.id"), primary_key=True),
)


#TODO: Add uuid style external ids
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    loans: Mapped[List[Loan]] = relationship(
        secondary=association_table, back_populates="loans"
    )

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    term = Column(Integer)
    interest_rate = Column(Float)
    parents: Mapped[List[User]] = relationship(
        secondary=association_table, back_populates="users"
    )


class LoanMonth(Base):
    __tablename__ = "loan_months"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer)
    principle_amount = Column(Numeric(scale=2))
    interest_amount = Column(Numeric(scale=2))
    loan_id = Column(Integer, ForeignKey("loans.id"))
    loan = relationship("Loan", back_populates="loan_months")
    __table_args__ = (UniqueConstraint('loan_id', 'month', name='_loan_month_uc'),
                     )