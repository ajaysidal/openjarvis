from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from silas.connectors.oauth import save_tokens, require_access_token, _CONNECTORS_DIR

router = APIRouter()

@router.get("/api/auth/callback/github")
async def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing ?code")

    # TODO: Replace with per-user/workspace resolution
    client_id = "Ov23liqLsvIdG7NsdVv0"
    client_secret = "8bb8f0a035bc39667133e78889f34051d6381853"

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data=data,
            headers=headers,
        )

    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail="GitHub token exchange failed")

    tokens = resp.json()
    access_token = require_access_token(tokens)

    payload = {
        "access_token": access_token,
        "refresh_token": tokens.get("refresh_token", ""),
        "token_type": tokens.get("token_type", "Bearer"),
        "expires_in": tokens.get("expires_in", 3600),
        "client_id": client_id,
        "client_secret": client_secret,
    }

    save_tokens(str(_CONNECTORS_DIR / "github.json"), payload)

    return JSONResponse({"ok": True})
