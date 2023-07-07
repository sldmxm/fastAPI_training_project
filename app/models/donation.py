from sqlalchemy import (
    Column, ForeignKey, Integer, Text
)

from .abstract import ProjectAndDonationAbstractModel


class Donation(ProjectAndDonationAbstractModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __str__(self):
        return f'<Donation {self.id}>'

    def __repr__(self):
        return f'<Donation {self.id}> amount: {self.full_amount}>'
