#!/usr/bin/env python3
"""初始化管理员账号."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash


def init_admin(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123",
    full_name: str = "系统管理员",
):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"管理员 '{username}' 已存在，跳过创建")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_admin=True,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"管理员 '{username}' 创建成功 (id={admin.id})")
        print(f"邮箱: {email}")
        print(f"密码: {password}")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="初始化管理员账号")
    parser.add_argument("--username", default="admin", help="管理员用户名")
    parser.add_argument("--email", default="admin@example.com", help="管理员邮箱")
    parser.add_argument("--password", default="admin123", help="管理员密码")
    parser.add_argument("--full-name", default="系统管理员", help="管理员姓名")
    args = parser.parse_args()

    init_admin(args.username, args.email, args.password, args.full_name)
