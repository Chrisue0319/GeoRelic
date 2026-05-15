from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.utils.exceptions import ServiceException, ErrorCode


def _build_error_response(
    error_code: str,
    error_desc: str,
    status_code: int,
    debug_info: str | None = None,
) -> dict:
    return {
        "error_code": error_code,
        "error_desc": error_desc,
        "debug_info": debug_info,
        "status_code": status_code,
    }


def service_exception_handler(request: Request, exc: ServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_response(
            error_code=exc.error_code,
            error_desc=exc.error_desc,
            status_code=exc.status_code,
            debug_info=exc.debug_info,
        ),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', '')}")
    debug_info = "; ".join(errors) if errors else None

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_response(
            error_code=ErrorCode.VALIDATION_ERROR[0],
            error_desc=ErrorCode.VALIDATION_ERROR[1],
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            debug_info=debug_info,
        ),
    )


def http_exception_handler(request: Request, exc):
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_response(
                error_code=ErrorCode.NOT_FOUND[0] if exc.status_code == 404 else f"HTTP_{exc.status_code}",
                error_desc=str(exc.detail),
                status_code=exc.status_code,
                debug_info=f"Request path: {request.url.path}",
            ),
        )
    return None


def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_response(
            error_code=ErrorCode.INTERNAL_ERROR[0],
            error_desc=ErrorCode.INTERNAL_ERROR[1],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            debug_info=str(exc),
        ),
    )


def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_response(
            error_code=ErrorCode.INTERNAL_ERROR[0],
            error_desc=ErrorCode.INTERNAL_ERROR[1],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            debug_info=str(exc) if hasattr(exc, "__str__") else "Unknown error",
        ),
    )
