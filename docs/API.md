# API 接口文档

## 基础信息

- 基础 URL：`http://localhost:8000/api/v1`
- 认证方式：Bearer Token 或 API Key
- 所有时间戳格式：ISO 8601（`YYYY-MM-DDTHH:MM:SS`）
- 默认分页：`limit=20`, `skip=0`

## 认证

### POST /auth/register

用户注册。

**请求体：**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User"
}
```

**响应（201）：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**错误响应：**
```json
{
  "error_code": "AUTH_004",
  "error_desc": "用户名已被注册",
  "debug_info": "Username 'testuser' is already taken",
  "status_code": 400
}
```

---

### POST /auth/login

用户登录。

**请求体：** `application/x-www-form-urlencoded`
- `username`: 用户名
- `password`: 密码

**响应（200）：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 用户

### GET /users/me

获取当前用户信息。

**请求头：** `Authorization: Bearer <token>`

**响应（200）：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_admin": false,
  "api_key": null,
  "api_key_created_at": null,
  "created_at": "2026-05-15T10:00:00",
  "updated_at": "2026-05-15T10:00:00"
}
```

---

### PUT /users/me

更新个人信息。

**请求头：** `Authorization: Bearer <token>`

**请求体：**
```json
{
  "email": "new@example.com",
  "full_name": "New Name",
  "password": "newpassword123"
}
```

**响应（200）：** 更新后的用户信息

---

### POST /users/api-key

生成 API Key（用于公开查询，无需频繁登录）。

**请求头：** `Authorization: Bearer <token>`

**响应（200）：**
```json
{
  "api_key": "aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"
}
```

---

## POI（文物保护单位）

### GET /pois/

查询 POI 列表（支持多种过滤条件）。

**请求头：** `Authorization: Bearer <token>` 或在 URL 中附加 `?api_key=<key>`

**查询参数：**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| name | string | 按名称模糊查询 | `故宫` |
| province | string | 按省份模糊查询 | `山西` |
| type | string | 按类别精确匹配 | `古建筑` |
| batch | string | 按批次精确匹配 | `第一批` |
| min_lon | float | 最小经度（拉框查询） | `100.0` |
| max_lon | float | 最大经度（拉框查询） | `120.0` |
| min_lat | float | 最小纬度（拉框查询） | `20.0` |
| max_lat | float | 最大纬度（拉框查询） | `40.0` |
| center_lon | float | 中心点经度（半径查询） | `116.4` |
| center_lat | float | 中心点纬度（半径查询） | `39.9` |
| radius_km | float | 半径（公里，半径查询） | `50` |
| has_image | boolean | 是否有图片 | `true` |
| has_website | boolean | 是否有官网 | `true` |
| skip | integer | 跳过条数 | `0` |
| limit | integer | 返回条数（最大 100） | `20` |

**响应（200）：**
```json
[
  {
    "id": 1,
    "code": 404,
    "class_code": "210",
    "name": "喜洲白族古建筑群",
    "age": "明、清",
    "address": "云南省大理市",
    "type": "古建筑",
    "batch": "第五批",
    "remark": null,
    "bd_lon": 100.134614,
    "bd_lat": 25.856669,
    "lon": 100.126760,
    "lat": 25.853924,
    "image_url": null,
    "website": null,
    "created_at": "2026-05-15T10:00:00",
    "updated_at": "2026-05-15T10:00:00"
  }
]
```

---

### GET /pois/{poi_id}

查询单个 POI 详情。

**请求头：** `Authorization: Bearer <token>` 或 `?api_key=<key>`

**路径参数：**
- `poi_id`: POI ID

**响应（200）：** POI 详情对象

**错误响应：**
```json
{
  "error_code": "POI_001",
  "error_desc": "POI 不存在",
  "debug_info": "POI with id=99999 does not exist",
  "status_code": 404
}
```

---

### GET /pois/types/list

获取所有 POI 类别列表。

**响应（200）：**
```json
["古建筑", "古遗址", "古墓葬", "石窟寺及石刻", "近现代重要史迹及代表性建筑", "其他"]
```

---

### GET /pois/batches/list

获取所有 POI 批次列表。

**响应（200）：**
```json
["第一批", "第二批", "第三批", "第四批", "第五批", "第六批", "第七批"]
```

---

### POST /pois/

创建 POI（**管理员权限**）。

**请求头：** `Authorization: Bearer <token>`（需管理员）

**请求体：**
```json
{
  "code": 123,
  "name": "测试文物",
  "address": "北京市",
  "type": "古建筑",
  "lon": 116.4,
  "lat": 39.9,
  "image_url": "https://example.com/image.jpg",
  "website": "https://example.com"
}
```

**响应（201）：** 创建的 POI 对象

**错误响应（权限不足）：**
```json
{
  "error_code": "AUTH_002",
  "error_desc": "权限不足",
  "debug_info": "Admin privileges required for this operation",
  "status_code": 403
}
```

---

### PUT /pois/{poi_id}

更新 POI（**管理员权限**）。

**请求头：** `Authorization: Bearer <token>`（需管理员）

**请求体：**（字段可选，仅更新提供的字段）
```json
{
  "name": "更新后的名称",
  "address": "更新后的地址"
}
```

**响应（200）：** 更新后的 POI 对象

---

### DELETE /pois/{poi_id}

删除 POI（**管理员权限**）。

**请求头：** `Authorization: Bearer <token>`（需管理员）

**响应（204）：** 无内容

---

## 错误代码对照表

| 错误代码 | 说明 | HTTP 状态 |
|----------|------|-----------|
| AUTH_001 | 认证失败，凭据无效 | 401 |
| AUTH_002 | 权限不足 | 403 |
| AUTH_003 | 用户不存在 | 401 |
| AUTH_004 | 用户名已被注册 | 400 |
| AUTH_005 | 邮箱已被注册 | 400 |
| AUTH_006 | 用户已被禁用 | 403 |
| RATE_001 | 请求频率超限 | 429 |
| POI_001 | POI 不存在 | 404 |
| VAL_001 | 请求参数校验失败 | 422 |
| SYS_001 | 请求的资源不存在 | 404 |
| SYS_002 | 系统内部错误 | 500 |
