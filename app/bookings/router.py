from datetime import date

from fastapi import APIRouter, Request, Depends, BackgroundTasks
from pydantic import parse_obj_as

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
async def add_booking(
        background_tasks: BackgroundTasks,
        room_id: int,
        date_from: date,
        date_to: date,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(
        user.id,
        room_id,
        date_from,
        date_to)
    booking_dict = parse_obj_as(SBooking, booking).dict()
    # celery variant:
    # send_booking_confirmation_email.delay(booking_dict, user.email)
    # background tasks variant:
    background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    if not booking:
        raise RoomCannotBeBooked
    return booking_dict
