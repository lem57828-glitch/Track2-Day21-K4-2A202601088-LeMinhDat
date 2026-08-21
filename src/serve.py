import os

import boto3
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

ARTIFACT_BUCKET = os.environ["ARTIFACT_BUCKET"]
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """Tai model.joblib tu cloud storage ve may khi server khoi dong."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    client = boto3.client("s3")
    client.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)
    print(f"Da tai model tu s3://{ARTIFACT_BUCKET}/{MODEL_KEY} ve {MODEL_PATH}")


download_model()
model = joblib.load(MODEL_PATH)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """GitHub Actions goi endpoint nay sau khi trien khai de xac nhan server song."""
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Dau vao: JSON {"features": [f1, f2, ..., f10]}
    Dau ra:  JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}
    """
    if len(req.features) != 10:
        raise HTTPException(status_code=400, detail="features phai co dung 10 gia tri")

    pred = int(model.predict([req.features])[0])
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"
    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
