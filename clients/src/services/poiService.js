import { mockPois } from '../mock/pois';

const API_BASE_URL = import.meta.env.VITE_POI_API_BASE_URL;

export async function fetchPois(query = {}) {
  if (!API_BASE_URL) {
    return filterMockPois(query);
  }

  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, value);
    }
  });

  const response = await fetch(`${API_BASE_URL}/pois?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`POI 服务请求失败：${response.status}`);
  }

  const result = await response.json();
  return Array.isArray(result) ? result : result.data ?? [];
}

function filterMockPois({ keyword = '', category = '' }) {
  const normalizedKeyword = keyword.trim().toLowerCase();
  return mockPois.filter((poi) => {
    const matchKeyword =
      !normalizedKeyword ||
      poi.name.toLowerCase().includes(normalizedKeyword) ||
      poi.address.toLowerCase().includes(normalizedKeyword);
    const matchCategory = !category || poi.category === category;
    return matchKeyword && matchCategory;
  });
}
