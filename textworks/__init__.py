from transformers import TrainerCallback
import os
from typing import Dict, Any, Optional 
import httpx
from urllib.parse import urljoin
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from functools import wraps

# Load all env vars before starting
load_dotenv()

ENV_VAR_API_KEY = "TEXTWORKS_API_KEY"
ENV_VAR_TEXTWORKS_URL = "TEXTWORKS_URL"

TEXTWORKS_URL = "https://text.works/api/"
if ENV_VAR_TEXTWORKS_URL in os.environ:
    TEXTWORKS_URL = os.environ[ENV_VAR_TEXTWORKS_URL]

def req_url(path: str) -> str:
    return urljoin(TEXTWORKS_URL, path)

def requires_apikey(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.api_key is None:
            raise ValueError("No API key found. Either set the TEXTWORKS_API_KEY environment variable or log in with `textworks login`.")
        return method(self, *args, **kwargs)
    return wrapper

class TextworksLogger:
    def __init__(self, run_id: str, api_key: Optional[str] = None):
        self.init(run_id, api_key)

    def init(self, run_id: str, api_key: Optional[str]):
        if api_key is None:
            if ENV_VAR_API_KEY in os.environ:
                api_key = os.environ[ENV_VAR_API_KEY]

        if api_key is None:
            raise ValueError(
                "No API key found. Either set the TEXTWORKS_API_KEY environment variable or log in with `textworks login`."
            )

        self.api_key = api_key
        self.run_id = run_id
        self.step = 0

    @requires_apikey
    def health_check(self) -> bool:
        response = httpx.get(req_url("projects"), headers={"Authorization": f"Bearer {self.api_key}"})
        return response.status_code == 200

    @requires_apikey
    def log(
        self,
        data: Dict[str, int],
        step: Optional[int] = None,
        commit: Optional[bool] = None
    ) -> None:
        if step is None:
            step = self.step

        now = datetime.now().astimezone(ZoneInfo("UTC")).isoformat()
        http_data = {
            "time": now,
            "step": step,
            "metrics": data,
        }

        put_url = req_url(f"run/{self.run_id}/timeseries")
        response = httpx.put(
            put_url,
            json=http_data,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to log data: {response.text}")

        if commit:
            self.step += 1

    @requires_apikey
    def get_logs(self) -> Dict[str, Any]:
        response = httpx.get(
            req_url(f"run/{self.run_id}/timeseries"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get logs: {response.text}")

        return response.json()

    def commit(self):
        self.step += 1
