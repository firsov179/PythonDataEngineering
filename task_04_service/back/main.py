import os
import uuid
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

CSV_PATH = os.path.join(os.path.dirname(__file__), "RU_Electricity_Market_PZ_dayahead_price_volume.csv")

app = FastAPI()


class Record(BaseModel):
    timestep: str
    consumption_eur: float
    consumption_sib: float
    price_eur: float
    price_sib: float

    @validator("consumption_eur", "consumption_sib", "price_eur", "price_sib")
    def not_negative(cls, v):
        if v < 0:
            raise ValueError("Значение не может быть отрицательным")
        return v


def read_csv():
    df = pd.read_csv(CSV_PATH)
    if "id" not in df.columns:
        df.insert(0, "id", [str(uuid.uuid4()) for _ in range(len(df))])
        df.to_csv(CSV_PATH, index=False)
    return df


def write_csv(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False)


@app.get("/records")
def get_records():
    try:
        df = read_csv()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Файл с данными не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"count": len(df), "data": df.to_dict(orient="records")}


@app.post("/records", status_code=201)
def add_record(record: Record):
    try:
        df = read_csv()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Файл с данными не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    new_row = {"id": str(uuid.uuid4()), **record.dict()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    try:
        write_csv(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось сохранить данные: {e}")

    return new_row


@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    try:
        df = read_csv()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Файл с данными не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if record_id not in df["id"].values:
        raise HTTPException(status_code=404, detail=f"Запись {record_id} не найдена")

    df = df[df["id"] != record_id].reset_index(drop=True)

    try:
        write_csv(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось сохранить данные: {e}")

    return {"deleted": record_id}
