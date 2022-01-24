import requests
from requests.auth import AuthBase
from requests.models import PreparedRequest
from requests.models import Response


class ShortcutAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Shortcut-Token"] = self.token
        return r


class ShortcutClient:
    def __init__(self, api_token: str):
        self.auth = ShortcutAuth(api_token)

    def _call(
        self,
        method: str,
        path: str,
        data: dict | None = None,
        params: dict | None = None,
        *args,
        **kwargs,
    ) -> Response:
        return requests.request(
            method,
            url="https://api.app.shortcut.com/api/v3" + path,
            auth=self.auth,
            data=data,
            params=params,
        )

    def get(self, path: str, params: dict | None = None) -> Response:
        return self._call("GET", path, params=params)

    def get_labels(self) -> list[dict]:
        return self.get("/labels").json()

    def get_iteration_by_name(self, name: str) -> dict | None:
        resp = self.get("/iterations")
        matching = [i for i in resp.json() if i["name"] == name]
        if not matching:
            return None

        return matching[0]

    def get_iteration_stories(self, iteration_id) -> list[dict]:
        resp = self.get(f"/iterations/{iteration_id}/stories")
        return resp.json()

    def get_stories(self, story_ids: list[str], with_history: bool = False) -> list[dict]:
        stories = []

        for story_id in story_ids:
            story = self.get(f"/stories/{story_id}").json()

            if with_history:
                history = self.get(f"/stories/{story_id}/history").json()
                story["history"] = history

            stories.append(story)

        return stories
