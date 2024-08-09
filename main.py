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


@app.get("/{path:path}", status_code=200)
async def proxy(response: Response, request: Request, path: str):
    try:
        # 동적으로 생성된 URL
        api_url = f"https://ch.tetr.io/api/{path}"
        # 쿼리 스트링을 그대로 전달
        query_params = dict(request.query_params)

        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, params=query_params)

        # 응답의 상태 코드 설정
        response.status_code = res.status_code

        # 원본 응답 헤더 복사 (중복될 수 있는 헤더는 제외)
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        for name, value in res.headers.items():
            if name.lower() not in excluded_headers:
                response.headers[name] = value

        # 원본 응답 데이터를 클라이언트에게 반환
        return Response(content=res.content, media_type=res.headers.get("content-type"))
    except httpx.HTTPStatusError as e:
        response.status_code = e.response.status_code
        return {"error": "HTTP Error", "details": str(e)}
    except Exception as e:
        response.status_code = 500
        return {"error": "Internal Server Error", "details": str(e)} 
