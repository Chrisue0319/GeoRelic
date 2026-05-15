#!/usr/bin/env python3
"""导入全国文保单位数据到数据库."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.poi import POI


def import_data(excel_path: str, db: Session):
    df = pd.read_excel(excel_path)
    print(f"读取到 {len(df)} 条记录")

    count = 0
    for _, row in df.iterrows():
        poi = POI(
            code=int(row["code"]) if pd.notna(row.get("code")) else None,
            class_code=str(row["classCode"]) if pd.notna(row.get("classCode")) else None,
            name=str(row["name"]) if pd.notna(row.get("name")) else None,
            age=str(row["age"]) if pd.notna(row.get("age")) else None,
            address=str(row["add"]) if pd.notna(row.get("add")) else None,
            type=str(row["type"]) if pd.notna(row.get("type")) else None,
            batch=str(row["batch"]) if pd.notna(row.get("batch")) else None,
            remark=str(row["remark"]) if pd.notna(row.get("remark")) else None,
            bd_lon=float(row["bd_lon"]) if pd.notna(row.get("bd_lon")) else None,
            bd_lat=float(row["bd_lat"]) if pd.notna(row.get("bd_lat")) else None,
            lon=float(row["lon"]) if pd.notna(row.get("lon")) else None,
            lat=float(row["lat"]) if pd.notna(row.get("lat")) else None,
        )
        db.add(poi)
        count += 1
        if count % 100 == 0:
            db.commit()
            print(f"已导入 {count} 条...")

    db.commit()
    print(f"导入完成，共 {count} 条记录")


if __name__ == "__main__":
    default_path = "../../全国文保单位/全国文保单位.xlsx"
    excel_path = sys.argv[1] if len(sys.argv) > 1 else default_path

    if not os.path.exists(excel_path):
        print(f"文件不存在: {excel_path}")
        print(f"用法: python scripts/import_data.py [excel文件路径]")
        sys.exit(1)

    db = SessionLocal()
    try:
        import_data(excel_path, db)
    finally:
        db.close()
