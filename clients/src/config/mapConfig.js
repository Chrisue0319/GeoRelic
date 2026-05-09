export const amapConfig = {
  key: import.meta.env.VITE_AMAP_KEY,
  securityJsCode: import.meta.env.VITE_AMAP_SECURITY_JS_CODE,
  version: '2.0',
  plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.Geolocation'],
  defaultCenter: [116.397428, 39.90923],
  defaultZoom: 12,
};
