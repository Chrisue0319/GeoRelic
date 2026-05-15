# 部署与使用文档

## 环境要求

- Python 3.10+
- PostgreSQL 16+
- PostGIS 3.4+
- Git

## 安装步骤

### 1. 安装 PostgreSQL 与 PostGIS

```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib postgis
```

创建数据库用户和数据库：

```bash
sudo -u postgres createuser -s $(whoami)
sudo -u postgres createdb lbs_poi
psql -d lbs_poi -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 2. 配置数据库认证

编辑 PostgreSQL 认证配置：

```bash
sudo sed -i 's/scram-sha-256/trust/g' /etc/postgresql/16/main/pg_hba.conf
sudo systemctl restart postgresql
```

### 3. 安装 Python 依赖

```bash
cd webapiservices
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量模板并修改：

```bash
cp .env.example .env
```

主要配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `postgresql://user@localhost:5432/lbs_poi` |
| `SECRET_KEY` | JWT 签名密钥 | 生产环境必须修改 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分钟） | 30 |
| `RATE_LIMIT_PER_MINUTE` | 每分钟请求限制 | 60 |

### 5. 导入数据

```bash
python3 scripts/import_data.py /path/to/全国文保单位.xlsx
```

### 6. 初始化管理员

```bash
python3 scripts/init_admin.py --username admin --password yourpassword
```

### 7. 启动服务

开发模式：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

生产模式：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 使用说明

### 获取 API 文档

服务启动后访问：

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- OpenAPI JSON：`http://localhost:8000/openapi.json`

### 认证流程

1. **注册账号**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"yourname","email":"you@example.com","password":"yourpass"}'
   ```

2. **登录获取 Token**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=yourname&password=yourpass"
   ```

3. **使用 Token 访问 API**
   ```bash
   curl "http://localhost:8000/api/v1/pois/?limit=10" \
     -H "Authorization: Bearer <your_access_token>"
   ```

4. **获取 API Key**（用于公开查询）
   ```bash
   curl -X POST "http://localhost:8000/api/v1/users/api-key" \
     -H "Authorization: Bearer <your_access_token>"
   ```

5. **使用 API Key 查询**
   ```bash
   curl "http://localhost:8000/api/v1/pois/?limit=10&api_key=<your_api_key>"
   ```

## 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 初始化迁移环境
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```
