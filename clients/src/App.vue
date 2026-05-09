<script setup>
import MapView from './components/MapView.vue';
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">LBS 课程设计</p>
        <h1>GeoRelic 文保 POI 地图</h1>
      </div>
      <span class="status-pill">地图底座</span>
    </header>

    <MapView />
  </main>
</template>
