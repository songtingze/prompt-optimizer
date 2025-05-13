import sys
import traceback

from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# from config import config
from models.discriminative_task import ResponseWrapper
from utils.logger import TraceID, logger
from router import discriminative_task_router

app = FastAPI(
    title="Prompt Optimizer API",
    description="提示词优化API服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def uncaught_exception(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()

        extracted_tb = traceback.extract_tb(exc_traceback)

        full_log_message = f"{str(e)}\n{traceback.format_exc()}"

        if extracted_tb:
            last_frame = extracted_tb[-1]
            logger.patch(lambda record: record.update(
                file=last_frame.filename,
                line=last_frame.lineno,
                function=last_frame.name
            )).error(full_log_message)

        else:
            logger.error(f"未知异常: {full_log_message}")
        return JSONResponse(
            status_code=500,
            content=ResponseWrapper(
                code="500",
                msg=str(e)
            ).dict(),
        )


@app.middleware("http")
async def request_received(request, call_next):
    TraceID.set(TraceID.get())
    logger.info(f"请求: {request.url}")
    return await call_next(request)


app.include_router(discriminative_task_router)


def start():
    import uvicorn
    uvicorn.run(app="app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start()
