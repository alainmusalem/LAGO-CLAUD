// Single source of truth for timing (seconds). Narration cues come from the real ElevenLabs track (see work/tr.json).
export const FPS = 30;
export const TOTAL_SECONDS = 70;
export const GOLD = '#C9A24B';
export const NAVY = '#050B1A';

export type Cam = {s: [number, number]; x?: [number, number]; y?: [number, number]; r?: [number, number]; o?: [number, number]};
export type ShotDef = {id: string; img: string; from: number; to: number; cam: Cam; sweep?: boolean; dust?: number; grade?: 'cold' | 'warm' | 'analog'};

export const SHOTS: ShotDef[] = [
  // ESCENA 1 — el nuevo agente (sin marca)
  {id: '1a', img: 'silhouette', from: 0.0, to: 3.2, cam: {s: [1.04, 1.32], y: [0, 40], o: [50, 52]}, dust: 34},
  {id: '1b', img: 'desk', from: 3.0, to: 6.4, cam: {s: [1.12, 1.0], x: [50, -50], y: [20, -10]}, dust: 30},
  {id: '1c', img: 'city', from: 6.2, to: 9.6, cam: {s: [1.0, 1.18], y: [0, -70]}, dust: 18},
  // ESCENA 2 — el conflicto
  {id: '2a', img: 'arch', from: 9.4, to: 13.0, cam: {s: [1.0, 1.28], x: [40, -30], o: [38, 55]}, dust: 22},
  {id: '2b', img: 'seamaster', from: 12.8, to: 14.5, cam: {s: [2.5, 2.8], o: [50, 24]}, sweep: true},
  {id: '2c', img: 'city', from: 14.3, to: 17.5, cam: {s: [1.5, 1.75], x: [-60, 20], o: [28, 62]}, dust: 14},
  {id: '2d', img: 'reverso', from: 17.3, to: 20.8, cam: {s: [1.9, 2.15], o: [50, 46]}, sweep: true},
  {id: '2e', img: 'silhouette', from: 20.6, to: 24.9, cam: {s: [1.55, 1.12], x: [30, -30], o: [50, 58]}, dust: 30},
  // ESCENA 3 — Omega Seamaster Diver 300M
  {id: '3a', img: 'underwater', from: 24.7, to: 27.2, cam: {s: [1.0, 1.14], y: [0, -50]}, dust: 55},
  {id: '3b', img: 'seamaster', from: 27.0, to: 30.2, cam: {s: [0.8, 0.9], y: [110, 70], r: [-2, 1.5], o: [50, 50]}, sweep: true, dust: 20},
  {id: '3c', img: 'seamaster', from: 30.0, to: 32.5, cam: {s: [2.25, 2.55], r: [1.5, -1.5], o: [50, 49]}, sweep: true},
  {id: '3d', img: 'seamaster', from: 32.3, to: 35.0, cam: {s: [2.0, 2.25], x: [0, -30], o: [74, 60]}, sweep: true, dust: 24},
  // ESCENA 4 — Jaeger-LeCoultre Polaris
  {id: '4a', img: 'arch', from: 34.8, to: 37.7, cam: {s: [1.2, 1.0], x: [-40, 40], o: [30, 55]}, dust: 22},
  {id: '4b', img: 'polaris', from: 37.5, to: 40.2, cam: {s: [0.8, 0.9], x: [-20, 20], y: [110, 70], o: [48, 47]}, sweep: true, dust: 18},
  {id: '4c', img: 'polaris', from: 40.0, to: 43.2, cam: {s: [2.1, 2.45], o: [50, 44]}, sweep: true},
  // ESCENA 5 — Reverso
  {id: '5a', img: 'city', from: 43.0, to: 46.9, cam: {s: [1.25, 1.0], x: [40, -40], o: [50, 60]}, dust: 24},
  {id: '5c', img: 'reverso', from: 50.0, to: 51.6, cam: {s: [2.2, 2.45], o: [50, 40]}, sweep: true},
  {id: '5d', img: 'city', from: 51.4, to: 52.8, cam: {s: [1.2, 1.36], y: [0, -50], o: [50, 62]}, dust: 30},
  // ESCENA 6 — 1962 (textura analógica)
  {id: '6a', img: 'terrace', from: 52.6, to: 57.6, cam: {s: [1.0, 1.2], x: [30, -30], y: [10, -20], o: [45, 55]}, grade: 'analog'},
  {id: '6b', img: 'vintage', from: 57.4, to: 60.5, cam: {s: [0.8, 0.9], y: [110, 70], r: [-1, 1], o: [47, 46]}, sweep: true, grade: 'analog'},
];

// Reverso flip card (no internal mechanism is shown): background + card timing
export const FLIP = {from: 46.7, to: 50.2, flipAt: 47.1, flipBackAt: 48.9};
// Finale: three candidates revealed progressively
export const FINALE = {from: 60.3, to: 70.0, seamaster: 63.9, polaris: 66.9, reverso: 67.5};
