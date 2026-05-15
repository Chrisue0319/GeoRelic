<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as THREE from 'three';
import earthTextureUrl from '../Assets/image.png';

const props = defineProps({
  center: {
    type: Object,
    default: () => ({
      longitude: 116.397428,
      latitude: 39.90923,
    }),
  },
  active: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['zoom-in', 'center-change']);

const globeRef = ref(null);

let renderer;
let scene;
let camera;
let globe;
let atmosphere;
let animationFrameId;
let needsRender = true;
let resizeObserver;
let isDragging = false;
let lastPointerX = 0;
let lastPointerY = 0;
let globeZoom = 1;
let centerLongitude = props.center.longitude;
let centerLatitude = clampLatitude(props.center.latitude);

const baseCameraDistance = 5.6;

onMounted(() => {
  initScene();
  resizeScene();
  animate();
});

watch(
  () => props.center,
  (center) => {
    if (isDragging) {
      return;
    }

    centerLongitude = center.longitude;
    centerLatitude = clampLatitude(center.latitude);
    updateGlobeRotation();
  },
  { deep: true },
);

watch(
  () => props.active,
  (active) => {
    if (!active) {
      return;
    }

    globeZoom = 1;
    if (camera) {
      camera.position.z = getCameraDistance();
    }

    needsRender = true;
    requestAnimationFrame(resizeScene);
  },
);

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeScene);

  if (resizeObserver) {
    resizeObserver.disconnect();
  }

  cancelAnimationFrame(animationFrameId);

  if (globe) {
    globe.geometry.dispose();
    globe.material.map?.dispose();
    globe.material.dispose();
  }

  if (atmosphere) {
    atmosphere.geometry.dispose();
    atmosphere.material.dispose();
  }

  if (renderer) {
    renderer.dispose();
  }
});

function initScene() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
  camera.position.set(0, 0, getCameraDistance());

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance',
  });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  globeRef.value.appendChild(renderer.domElement);

  const texture = new THREE.TextureLoader().load(earthTextureUrl, () => {
    updateGlobeRotation();
  });
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  texture.wrapS = THREE.RepeatWrapping;

  globe = new THREE.Mesh(
    new THREE.SphereGeometry(1.45, 96, 64),
    new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.92,
      metalness: 0,
    }),
  );
  scene.add(globe);

  atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(1.49, 96, 64),
    new THREE.MeshBasicMaterial({
      color: 0x6ec8ff,
      transparent: true,
      opacity: 0.12,
      side: THREE.BackSide,
      blending: THREE.AdditiveBlending,
    }),
  );
  scene.add(atmosphere);

  const ambientLight = new THREE.AmbientLight(0xffffff, 1.55);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
  keyLight.position.set(-2.6, 2.4, 4.2);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0x8fd7ff, 1.25);
  rimLight.position.set(3.2, -1.2, -2.2);
  scene.add(rimLight);

  window.addEventListener('resize', resizeScene);
  resizeObserver = new ResizeObserver(resizeScene);
  resizeObserver.observe(globeRef.value);
  updateGlobeRotation();
}

function animate() {
  animationFrameId = requestAnimationFrame(animate);

  if (!renderer || !scene || !camera) {
    return;
  }

  if (!props.active && !needsRender) {
    return;
  }

  renderer.render(scene, camera);
  needsRender = false;
}

function resizeScene() {
  if (!renderer || !camera || !globeRef.value) {
    return;
  }

  const { width, height } = globeRef.value.getBoundingClientRect();
  if (width === 0 || height === 0) {
    return;
  }

  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  needsRender = true;
}

function updateGlobeRotation() {
  if (!globe || !atmosphere) {
    return;
  }

  const latitudeRotation = THREE.MathUtils.degToRad(centerLatitude);
  const longitudeRotation = THREE.MathUtils.degToRad(-centerLongitude - 90);

  globe.rotation.set(latitudeRotation, longitudeRotation, 0);
  atmosphere.rotation.copy(globe.rotation);
  needsRender = true;
}

function handlePointerDown(event) {
  isDragging = true;
  lastPointerX = event.clientX;
  lastPointerY = event.clientY;
  globeRef.value.setPointerCapture(event.pointerId);
}

function handlePointerMove(event) {
  if (!isDragging) {
    return;
  }

  const deltaX = event.clientX - lastPointerX;
  const deltaY = event.clientY - lastPointerY;
  rotateGlobe(deltaX);
  tiltGlobe(deltaY);
  updateGlobeRotation();
  emitCenterChange();
  lastPointerX = event.clientX;
  lastPointerY = event.clientY;
}

function handlePointerUp(event) {
  isDragging = false;
  if (globeRef.value.hasPointerCapture(event.pointerId)) {
    globeRef.value.releasePointerCapture(event.pointerId);
  }
}

function handleWheel(event) {
  event.preventDefault();

  if (event.deltaY < 0) {
    globeZoom += 0.08;
  } else {
    globeZoom -= 0.08;
  }

  globeZoom = Math.min(Math.max(globeZoom, 0.58), 1.55);
  camera.position.z = getCameraDistance();
  needsRender = true;

  if (globeZoom >= 1.5) {
    const center = getCurrentCenter();
    emit('center-change', center);
    emit('zoom-in', center);
  }
}

function emitCenterChange() {
  emit('center-change', getCurrentCenter());
}

function getCurrentCenter() {
  return {
    longitude: normalizeLongitude(centerLongitude),
    latitude: centerLatitude,
  };
}

function rotateGlobe(deltaX) {
  centerLongitude = normalizeLongitude(centerLongitude - deltaX * 0.35);
}

function tiltGlobe(deltaY) {
  centerLatitude = clampLatitude(centerLatitude + deltaY * 0.18);
}

function normalizeLongitude(longitude) {
  return ((((longitude + 180) % 360) + 360) % 360) - 180;
}

function clampLatitude(latitude) {
  const tropic = 23.436;
  return Math.min(Math.max(latitude, -tropic), tropic);
}

function getCameraDistance() {
  return baseCameraDistance / globeZoom;
}
</script>

<template>
  <div
    ref="globeRef"
    class="simple-globe"
    @pointerdown="handlePointerDown"
    @pointermove="handlePointerMove"
    @pointerup="handlePointerUp"
    @pointercancel="handlePointerUp"
    @wheel="handleWheel"
  />
</template>

<style scoped>
.simple-globe {
  width: 100%;
  height: 100%;
  min-height: 560px;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 45%, rgba(31, 60, 88, 0.48), transparent 38%),
    linear-gradient(135deg, #07111f, #111827);
  cursor: grab;
  touch-action: none;
}

.simple-globe:active {
  cursor: grabbing;
}

.simple-globe :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
