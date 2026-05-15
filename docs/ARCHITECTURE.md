# 系统架构设计

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      客户端层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Web 浏览器   │  │ 移动端 App   │  │ 地图客户端        │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
└─────────┼────────────────┼──────────────────┼───────────┘
          │                │                  │
          └────────────────┴──────────────────┘
                           │
                    HTTP/HTTPS
                           │
┌──────────────────────────┼──────────────────────────────┐
│                      API 服务层                          │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │                  FastAPI Application              │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │ 认证模块 │ │ 用户模块  │ │ POI模块 │  │ 限速模块 │  │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │  │
│  │       └───────────┴───────────┴───────────┘       │  │
│  │                    依赖注入层                       │  │
│  │         (get_db / get_current_user / 限速)         │  │
│  └────────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │                  数据访问层                         │  │
│  │              SQLAlchemy ORM + GeoAlchemy2         │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │                  数据存储层                         │  │
│  │         PostgreSQL 16 + PostGIS 3.4               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 模块划分

| 模块 | 职责 | 对应代码 |
|------|------|----------|
| 认证模块 | 用户注册、登录、JWT Token 签发 | `app/routers/auth.py` |
| 用户模块 | 个人信息维护、API Key 管理 | `app/routers/users.py` |
| POI 模块 | 文保单位数据的增删改查与空间查询 | `app/routers/poi.py` |
| 限速模块 | 基于用户身份请求频率控制 | `app/utils/rate_limit.py` |
| 安全模块 | 密码哈希、Token 编解码 | `app/utils/security.py` |

## 认证流程

```
┌──────────┐     注册/登录      ┌──────────┐     验证      ┌──────────┐
│  客户端   │ ────────────────→ │ 认证服务  │ ──────────→ │ 数据库   │
└──────────┘                   └──────────┘             └──────────┘
     │                              │
     │    ←──── access_token ────   │
     │                              │
     │    Bearer Token ──────────→  │
     │                              │
     │    ←──── 受保护资源 ───────  │
```

## 角色权限模型

| 角色 | 标识 | 权限 |
|------|------|------|
| 内部数据维护人员 | `is_admin = true` | POI 增删改查 + 用户管理 |
| 公众用户 | `is_admin = false` | POI 查询 + API Key 获取 + 个人信息维护 |
| 匿名用户 | 无认证 | 不可访问（所有接口需认证） |

## 数据库设计

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 用户 ID |
| username | VARCHAR(50) UNIQUE | 用户名 |
| email | VARCHAR(100) UNIQUE | 邮箱 |
| hashed_password | VARCHAR(200) | 密码哈希 |
| full_name | VARCHAR(100) | 姓名 |
| is_active | BOOLEAN | 是否启用 |
| is_admin | BOOLEAN | 是否为管理员 |
| api_key | VARCHAR(100) UNIQUE | API Key |
| api_key_created_at | TIMESTAMP | API Key 创建时间 |
| created_at | TIMESTAMP | 注册时间 |
| updated_at | TIMESTAMP | 更新时间 |

### pois 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | POI ID |
| code | INTEGER INDEX | 文保单位编号 |
| class_code | VARCHAR(50) INDEX | 分类编号 |
| name | VARCHAR(200) INDEX | 名称 |
| age | VARCHAR(200) | 年代 |
| address | VARCHAR(300) | 地址 |
| type | VARCHAR(50) INDEX | 类别 |
| batch | VARCHAR(20) INDEX | 批次 |
| remark | TEXT | 备注 |
| bd_lon | FLOAT | 百度经度 |
| bd_lat | FLOAT | 百度纬度 |
| lon | FLOAT INDEX | WGS84 经度 |
| lat | FLOAT INDEX | WGS84 纬度 |
| geom | GEOMETRY(POINT, 4326) | PostGIS 空间点 |
| image_url | VARCHAR(500) | 图片链接 |
| website | VARCHAR(500) | 官网地址 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 空间索引

PostGIS 为 `geom` 字段自动创建 GiST 空间索引，支持高效的：
- 点查询（ST_Intersects）
- 距离查询（ST_DWithin）
- 范围查询（ST_Within）

## 错误处理机制

所有异常统一通过 `ServiceException` 抛出，由全局异常处理器捕获并转换为标准响应格式：

```json
{
  "error_code": "POI_001",
  "error_desc": "POI 不存在",
  "debug_info": "POI with id=99999 does not exist",
  "status_code": 404
}
```

## 限速策略

| 操作类型 | 限制 | 窗口 |
|----------|------|------|
| 读操作（查询） | 60 次 | 60 秒 |
| 写操作（增删改） | 30 次 | 60 秒 |
| 认证操作（注册/登录） | 10 次 | 60 秒 |

限速键按优先级：`用户 ID` → `API Key` → `IP 地址`。
