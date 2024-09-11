from fastapi import FastAPI, Response, Request
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
@app.get("/{proxy_type:path}/{path:path}", status_code=200)
async def proxy(proxy_type: str, path: str, response: Response, request: Request):
    paths = path.split(",")
    proxy_path = '/'.join(paths)
    try:
        if proxy_type == "api":
            base_url = f"https://ch.tetr.io/api/{proxy_path}"
        elif proxy_type == "user-content":
            base_url = f"https://tetr.io/{proxy_path}"
        else:
            response.status_code = 404
            return {"error": "Not Found"}

        query_params = dict(request.query_params)
        async with httpx.AsyncClient() as client:
            res = await client.get(base_url, params=query_params)

        # 응답 내용을 로깅합니다
        print(f"Response status: {res.status_code}")
        print(f"Response content: {res.text}")

        response.status_code = res.status_code
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        for name, value in res.headers.items():
            if name.lower() not in excluded_headers:
                response.headers[name] = value

        return Response(content=res.content, media_type=res.headers.get("content-type"))
    except httpx.HTTPStatusError as e:
        response.status_code = e.response.status_code
        return {"error": "HTTP Error", "details": str(e)}
    except Exception as e:
        response.status_code = 500
        return {"error": "Internal Server Error", "details": str(e)}
