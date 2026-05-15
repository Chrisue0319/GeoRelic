from fastapi import HTTPException, status


class ErrorCode:
    AUTH_INVALID_CREDENTIALS = ("AUTH_001", "认证失败，凭据无效")
    AUTH_PERMISSION_DENIED = ("AUTH_002", "权限不足")
    AUTH_USER_NOT_FOUND = ("AUTH_003", "用户不存在")
    AUTH_USERNAME_EXISTS = ("AUTH_004", "用户名已被注册")
    AUTH_EMAIL_EXISTS = ("AUTH_005", "邮箱已被注册")
    AUTH_INACTIVE_USER = ("AUTH_006", "用户已被禁用")

    RATE_LIMIT_EXCEEDED = ("RATE_001", "请求频率超限，请稍后再试")

    POI_NOT_FOUND = ("POI_001", "POI 不存在")
    POI_CREATE_FAILED = ("POI_002", "POI 创建失败")
    POI_UPDATE_FAILED = ("POI_003", "POI 更新失败")
    POI_DELETE_FAILED = ("POI_004", "POI 删除失败")

    VALIDATION_ERROR = ("VAL_001", "请求参数校验失败")
    NOT_FOUND = ("SYS_001", "请求的资源不存在")
    INTERNAL_ERROR = ("SYS_002", "系统内部错误")


class ServiceException(HTTPException):
    def __init__(
        self,
        error_code: str,
        error_desc: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        debug_info: str | None = None,
    ):
        self.error_code = error_code
        self.error_desc = error_desc
        self.debug_info = debug_info
        super().__init__(status_code=status_code, detail=error_desc)


class AuthException(ServiceException):
    pass


class POIException(ServiceException):
    pass


class RateLimitException(ServiceException):
    pass
