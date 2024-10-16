from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache
from pydantic import parse_obj_as

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelInfo

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)


@router.get("/{location}")
@cache(expire=30)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
):
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    hotels_json = parse_obj_as(List[SHotelInfo], hotels)
    return hotels_json


@router.get("/id/{hotel_id}", include_in_schema=True)
async def get_hotel_by_id(
    hotel_id: int,
) -> Optional[SHotel]:
    return await HotelDAO.find_one_or_none(id=hotel_id)
