from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from typing import Annotated
from models import User
from schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    if users is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no users'
        )
    return users


@router.get("/{user_id}")
async def user_by_id(
        user_id: Annotated[int, Path(ge=1, le=100)],
        db: Annotated[Session, Depends(get_db)]
):
    current_user = db.scalars(select(User).where(User.id == user_id)).first()
    if current_user is not None:
        return current_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)],
                      create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)))

    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)],
                      user_id: Annotated[int, Path(ge=1, le=100)],
                      update_user: UpdateUser):
    current_user = db.scalars(select(User).where(User.id == user_id)).first()
    if current_user is not None:
        db.execute(update(User).where(User.id == user_id).values(
            username=update_user.username,
            firstname=update_user.firstname,
            lastname=update_user.lastname,
            age=update_user.age,
            slug=slugify(update_user.username)
        ))
        db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "transaction": "User update is successful!"
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user_value = db.scalar(select(User).where(User.id == user_id))
    if user_value is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User was deleted successful!'
    }