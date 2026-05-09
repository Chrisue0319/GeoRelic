# GeoRelic Client

GeoRelic 前端地图客户端，基于 Vue 3、Vite 和高德地图 JS API。

## 开发运行

```bash
npm install
npm run dev
```

默认开发地址为 `http://localhost:5173/`。

## 环境变量

本地使用 `.env.local` 配置高德地图 Key：

```bash
VITE_AMAP_KEY=your_amap_js_api_key
VITE_AMAP_SECURITY_JS_CODE=
VITE_POI_API_BASE_URL=
```

如果高德控制台为 Web端 Key 生成了安全密钥，将它填入
`VITE_AMAP_SECURITY_JS_CODE`。

`VITE_POI_API_BASE_URL` 为空时，前端使用 `src/mock/pois.js` 中的模拟 POI 数据。
后端服务完成后，将它配置为后端 API 地址即可，例如：

```bash
VITE_POI_API_BASE_URL=https://example.com/api
```

当前前端会请求：

```text
GET {VITE_POI_API_BASE_URL}/pois?keyword=...&category=...
```

后端返回格式可以是数组，也可以是 `{ "data": [...] }`。

## 目录说明

```text
src/components/MapView.vue     地图底座、筛选栏、POI Marker 展示
src/components/SimpleGlobe.vue  轻量 Canvas 地球仪视图
src/services/amapLoader.js     高德地图 JS API 加载器
src/services/poiService.js     POI 数据访问层，后续接后端主要改这里
src/mock/pois.js               后端未完成前的模拟数据
src/config/mapConfig.js        地图默认配置
```
