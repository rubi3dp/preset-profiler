"""Lädt preset_profiler.py als preset_profiler_any.py zu Orca Cloud hoch.

Läuft nur in GitHub Actions bei einem veröffentlichten Release. Anmeldung über
GitHubs OIDC-Token (Audience "orcacloud") – keine Passwörter oder Geheimnisse.
Voraussetzung: Repo ist im Orca-Cloud-Eintrag unter „GitHub publishing“ verbunden.
"""
import json
import os
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DATEI = "preset_profiler.py"
NAME_CLOUD = "preset_profiler_any.py"   # Orca Cloud verlangt eine Systemendung, _any = alle Systeme
API = "https://api.orcaslicer.com/api/v1/plugin-publish/releases"


def main():
    version = os.environ["GITHUB_REF_NAME"].removeprefix("v")
    changelog = (os.environ.get("CHANGELOG") or "").strip()[:4000]
    inhalt = open(DATEI, "rb").read()

    anfrage = Request(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"] + "&audience=orcacloud",
                      headers={"Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urlopen(anfrage, timeout=30) as antwort:
        token = json.load(antwort)["value"]
    print("::add-mask::" + token, flush=True)

    grenze = uuid.uuid4().hex
    meta = json.dumps({"version": version, "changelog": changelog})
    koerper = (
        f'--{grenze}\r\nContent-Disposition: form-data; name="metadata"\r\n\r\n{meta}\r\n'
        f'--{grenze}\r\nContent-Disposition: form-data; name="files"; filename="{NAME_CLOUD}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + inhalt + f"\r\n--{grenze}--\r\n".encode("ascii")
    anfrage = Request(API, data=koerper, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "multipart/form-data; boundary=" + grenze,
        # Ohne eigenen User-Agent blockt Cloudflare die Anfrage
        "User-Agent": f"preset-profiler-publisher/{version} (+https://github.com/rubi3dp/preset-profiler)",
    })
    try:
        with urlopen(anfrage, timeout=120) as antwort:
            if antwort.status != 201:
                raise SystemExit(f"Orca Cloud: HTTP {antwort.status}, erwartet 201")
    except HTTPError as fehler:
        text = fehler.read(16000).decode("utf-8", "replace")
        hinweis = {401: " – Repo nicht mit dem Orca-Cloud-Eintrag verbunden?",
                   }.get(fehler.code, "")
        raise SystemExit(f"Orca Cloud lehnt ab (HTTP {fehler.code}){hinweis}: {text}")
    print(f"Orca Cloud: Version {version} veröffentlicht")


if __name__ == "__main__":
    main()
