let loadingPromise;

export function loadAmap({ key, securityJsCode, version, plugins }) {
  if (window.AMap) {
    return Promise.resolve(window.AMap);
  }

  if (!key) {
    return Promise.reject(new Error('缺少高德地图 Key，请配置 VITE_AMAP_KEY'));
  }

  if (loadingPromise) {
    return loadingPromise;
  }

  if (securityJsCode) {
    window._AMapSecurityConfig = {
      securityJsCode,
    };
  }

  loadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const params = new URLSearchParams({
      v: version,
      key,
      plugin: plugins.join(','),
    });

    script.src = `https://webapi.amap.com/maps?${params.toString()}`;
    script.async = true;
    script.onload = () => {
      if (window.AMap) {
        resolve(window.AMap);
        return;
      }
      reject(new Error('高德地图脚本已加载，但 AMap 对象不可用'));
    };
    script.onerror = () => reject(new Error('高德地图脚本加载失败'));

    document.head.appendChild(script);
  });

  return loadingPromise;
}
