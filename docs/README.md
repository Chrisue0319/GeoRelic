# LBS POI Web API

基于位置的服务（Location-Based Service）专题 POI Web API，提供全国文物保护单位的位置信息查询与管理服务。

## 功能特性

- **RESTful API**：基于 FastAPI 构建，符合 REST 架构风格
- **用户认证**：支持 JWT Token 认证与 API Key 认证
- **角色权限**：区分内部数据维护人员（管理员）与公众用户
- **POI 查询**：支持按名称、省份、类别、批次、拉框范围、中心半径等多种条件查询
- **空间数据库**：基于 PostgreSQL + PostGIS，支持地理空间索引
- **访问限速**：基于用户身份的请求频率限制
- **统一错误响应**：包含业务错误代码、错误描述和调试信息

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 16 + PostGIS 3.4 |
| 认证 | JWT (python-jose) + bcrypt |
| 地理空间 | GeoAlchemy2 + Shapely |

## 项目结构

```
webapiservices/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── deps.py              # 依赖注入（认证、权限、限速）
│   ├── models/              # SQLAlchemy 数据模型
│   ├── schemas/             # Pydantic 数据校验
│   ├── routers/             # API 路由
│   ├── services/            # 业务逻辑层
│   └── utils/               # 工具函数
├── scripts/
│   ├── import_data.py       # 数据导入脚本
│   └── init_admin.py        # 管理员初始化脚本
├── alembic/                 # 数据库迁移
├── requirements.txt         # Python 依赖
└── .env                     # 环境变量配置
```

## 快速开始

详见 [DEPLOY.md](DEPLOY.md)。

## API 文档

详见 [API.md](API.md)。

## 系统架构

详见 [ARCHITECTURE.md](ARCHITECTURE.md)。
