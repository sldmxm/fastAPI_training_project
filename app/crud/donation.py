from app.crud.base import CRUDBase
from app.models import Donation


class CRUDDonation(CRUDBase):
    ...


donation_crud = CRUDDonation(Donation)
