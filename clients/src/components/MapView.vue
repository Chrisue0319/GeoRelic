<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import SimpleGlobe from './SimpleGlobe.vue';
import { amapConfig } from '../config/mapConfig';
import { loadAmap } from '../services/amapLoader';
import { fetchPois } from '../services/poiService';

const mapContainer = ref(null);
const keyword = ref('');
const selectedCategory = ref('');
const loading = ref(true);
const errorMessage = ref('');
const pois = ref([]);
const activeView = ref('map');
const globeCenter = ref({
  longitude: amapConfig.defaultCenter[0],
  latitude: amapConfig.defaultCenter[1],
});

let AMapInstance;
let map;
let infoWindow;
let markers = [];
let suppressGlobeSwitch = false;
let suppressGlobeSwitchTimer;
const viewTransitioning = ref(false);

const categories = computed(() => {
  return Array.from(new Set(pois.value.map((poi) => poi.category))).filter(Boolean);
});

onMounted(async () => {
  try {
    AMapInstance = await loadAmap(amapConfig);
    initMap();
    await refreshPois();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
});

onBeforeUnmount(() => {
  if (map) {
    map.destroy();
  }
});

async function refreshPois() {
  loading.value = true;
  errorMessage.value = '';

  try {
    pois.value = await fetchPois({
      keyword: keyword.value,
      category: selectedCategory.value,
    });
    renderPoiMarkers();
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
}

function initMap() {
  map = new AMapInstance.Map(mapContainer.value, {
    center: amapConfig.defaultCenter,
    zoom: amapConfig.defaultZoom,
    resizeEnable: true,
    viewMode: '2D',
  });

  map.addControl(new AMapInstance.Scale());
  map.addControl(new AMapInstance.ToolBar({ position: 'RT' }));

  const geolocation = new AMapInstance.Geolocation({
    position: 'RB',
    showMarker: true,
    showCircle: true,
    enableHighAccuracy: true,
  });
  map.addControl(geolocation);

  infoWindow = new AMapInstance.InfoWindow({
    offset: new AMapInstance.Pixel(0, -30),
  });

  map.on('zoomend', () => {
    if (suppressGlobeSwitch || activeView.value !== 'map') {
      return;
    }

    if (map.getZoom() <= 3) {
      switchView('globe');
    }
  });
}

function switchView(view, centerOverride) {
  if (view === activeView.value && !centerOverride) {
    return;
  }

  if (centerOverride) {
    updateGlobeCenter(centerOverride);
  }

  if (view === 'globe') {
    syncGlobeCenterFromMap();
  }

  viewTransitioning.value = true;
  activeView.value = view;
  window.setTimeout(() => {
    viewTransitioning.value = false;
  }, 260);

  if (view === 'map' && map) {
    suppressGlobeSwitch = true;
    window.clearTimeout(suppressGlobeSwitchTimer);
    nextTick(() => {
      requestAnimationFrame(() => {
        const nextCenter = [
          globeCenter.value.longitude,
          clamp(globeCenter.value.latitude, -84, 84),
        ];

        map.resize();
        map.setZoomAndCenter(4, nextCenter, false);
        map.once('zoomend', releaseGlobeSwitchSuppression);
        suppressGlobeSwitchTimer = window.setTimeout(releaseGlobeSwitchSuppression, 900);
      });
    });
  }
}

function syncGlobeCenterFromMap() {
  if (!map) {
    return;
  }

  const center = map.getCenter();
  globeCenter.value = {
    longitude: center.getLng(),
    latitude: center.getLat(),
  };
}

function updateGlobeCenter(center) {
  globeCenter.value = center;
}

function releaseGlobeSwitchSuppression() {
  window.clearTimeout(suppressGlobeSwitchTimer);
  suppressGlobeSwitch = false;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function renderPoiMarkers() {
  if (!map || !AMapInstance) {
    return;
  }

  map.remove(markers);
  markers = pois.value.map((poi) => {
    const marker = new AMapInstance.Marker({
      map,
      position: poi.position,
      title: poi.name,
      anchor: 'bottom-center',
    });

    marker.on('click', () => {
      infoWindow.setContent(createPoiInfoHtml(poi));
      infoWindow.open(map, poi.position);
    });

    return marker;
  });

  if (markers.length > 0) {
    map.setFitView(markers, false, [64, 64, 64, 64]);
  }
}

function createPoiInfoHtml(poi) {
  return `
    <section class="poi-window">
      <strong>${escapeHtml(poi.name)}</strong>
      <span>${escapeHtml(poi.category || '未分类')}</span>
      <p>${escapeHtml(poi.address || '')}</p>
      <p>${escapeHtml(poi.description || '')}</p>
    </section>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
</script>

<template>
  <section class="map-page">
    <aside class="map-panel">
      <div class="panel-heading">
        <h2>POI 图层</h2>
        <p>当前使用可替换的数据服务，后端完成后配置接口地址即可。</p>
      </div>

      <div class="view-switch" aria-label="地图视图切换">
        <button
          type="button"
          :class="{ active: activeView === 'map' }"
          @click="switchView('map')"
        >
          地图
        </button>
        <button
          type="button"
          :class="{ active: activeView === 'globe' }"
          @click="switchView('globe')"
        >
          地球
        </button>
      </div>

      <form class="filters" @submit.prevent="refreshPois">
        <label>
          关键词
          <input v-model="keyword" type="search" placeholder="名称或地址" />
        </label>

        <label>
          类别
          <select v-model="selectedCategory">
            <option value="">全部类别</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </label>

        <button type="submit" :disabled="loading">查询</button>
      </form>

      <div class="summary">
        <span>{{ loading ? '加载中' : `${pois.length} 个 POI` }}</span>
        <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
      </div>

      <ul class="poi-list">
        <li v-for="poi in pois" :key="poi.id">
          <strong>{{ poi.name }}</strong>
          <span>{{ poi.category }} · {{ poi.province }}</span>
        </li>
      </ul>
    </aside>

    <div class="map-stage" :class="{ transitioning: viewTransitioning }">
      <div
        ref="mapContainer"
        class="map-container view-layer"
        :class="{ active: activeView === 'map' }"
      />
      <div
        v-show="activeView === 'globe'"
        class="view-layer"
        :class="{ active: activeView === 'globe' }"
      >
        <SimpleGlobe
          :active="activeView === 'globe'"
          :center="globeCenter"
          @center-change="updateGlobeCenter"
          @zoom-in="switchView('map', $event)"
        />
      </div>
      <div v-if="errorMessage" class="map-error">{{ errorMessage }}</div>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  display: grid;
  flex: 1;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  min-height: 0;
}

.map-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
  border-right: 1px solid #d6dee2;
  overflow: auto;
  background: #ffffff;
}

.panel-heading h2 {
  margin: 0 0 6px;
  color: #14212b;
  font-size: 18px;
}

.panel-heading p {
  margin: 0;
  color: #607481;
  font-size: 14px;
  line-height: 1.6;
}

.filters {
  display: grid;
  gap: 12px;
}

.view-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  padding: 4px;
  border: 1px solid #d6dee2;
  border-radius: 8px;
  background: #f3f7f8;
}

.view-switch button {
  min-height: 34px;
  border: 0;
  border-radius: 6px;
  color: #405462;
  background: transparent;
  cursor: pointer;
}

.view-switch button.active {
  color: #ffffff;
  background: #197278;
}

.filters label {
  display: grid;
  gap: 6px;
  color: #405462;
  font-size: 14px;
}

.filters input,
.filters select {
  width: 100%;
  min-height: 38px;
  padding: 8px 10px;
  border: 1px solid #bfccd2;
  border-radius: 6px;
  color: #1f2937;
  background: #ffffff;
}

.filters button {
  min-height: 38px;
  border: 0;
  border-radius: 6px;
  color: #ffffff;
  background: #197278;
  cursor: pointer;
}

.filters button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.summary {
  display: grid;
  gap: 6px;
  color: #405462;
  font-size: 14px;
}

.error-text,
.map-error {
  color: #b42318;
}

.poi-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.poi-list li {
  display: grid;
  gap: 4px;
  padding: 12px;
  border: 1px solid #d6dee2;
  border-radius: 8px;
  background: #f8fbfc;
}

.poi-list strong {
  color: #14212b;
  font-size: 15px;
}

.poi-list span {
  color: #607481;
  font-size: 13px;
}

.map-stage {
  position: relative;
  min-height: 560px;
  overflow: hidden;
}

.map-container {
  width: 100%;
  height: 100%;
  min-height: 560px;
}

.view-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-height: 560px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 240ms ease;
}

.view-layer.active {
  opacity: 1;
  pointer-events: auto;
  z-index: 1;
}

.map-stage.transitioning .view-layer {
  transition-duration: 260ms;
}

.map-error {
  position: absolute;
  top: 16px;
  left: 50%;
  max-width: min(520px, calc(100% - 32px));
  padding: 10px 14px;
  border: 1px solid #f2b8b5;
  border-radius: 8px;
  background: #fff7f6;
  transform: translateX(-50%);
}

:global(.poi-window) {
  display: grid;
  gap: 4px;
  max-width: 260px;
  color: #1f2937;
  line-height: 1.45;
}

:global(.poi-window strong) {
  color: #14212b;
  font-size: 15px;
}

:global(.poi-window span) {
  color: #197278;
  font-size: 13px;
}

:global(.poi-window p) {
  margin: 0;
  color: #526774;
  font-size: 13px;
}

@media (max-width: 820px) {
  .map-page {
    grid-template-columns: 1fr;
  }

  .map-panel {
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid #d6dee2;
  }

  .map-stage,
  .map-container {
    min-height: 520px;
  }
}
</style>
