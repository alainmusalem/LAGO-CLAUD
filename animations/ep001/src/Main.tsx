import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, random, staticFile, useCurrentFrame} from 'remotion';
import {FINALE, FLIP, FPS, GOLD, NAVY, SHOTS, ShotDef, TOTAL_SECONDS} from './timeline';
import subs from './subtitles.json';

const W = 1080, H = 1920;
const f = (s: number) => Math.round(s * FPS);
const ease = Easing.bezier(0.45, 0, 0.2, 1);
const lerp = (p: number, r?: [number, number], d = 0) => (r ? r[0] + (r[1] - r[0]) * p : d);
const SANS = '"Inter Display","Inter",sans-serif';

// ---------- atmosphere ----------
const Dust: React.FC<{n: number; seed?: string}> = ({n, seed = 'd'}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {Array.from({length: n}).map((_, i) => {
        const x = random(`${seed}x${i}`) * W, sz = 1.5 + random(`${seed}s${i}`) * 3.5, sp = 6 + random(`${seed}v${i}`) * 22;
        const y = (((random(`${seed}y${i}`) * H - frame * sp * 0.5) % H) + H) % H;
        const tw = 0.25 + 0.55 * Math.abs(Math.sin(frame / (18 + random(`${seed}t${i}`) * 30) + i));
        return <div key={i} style={{position: 'absolute', left: x + Math.sin(frame / 40 + i) * 12, top: y, width: sz, height: sz, borderRadius: '50%',
          background: i % 5 === 0 ? GOLD : '#DDE6F5', opacity: tw * 0.55, filter: `blur(${sz > 3.5 ? 1.5 : 0.6}px)`}} />;
      })}
    </AbsoluteFill>
  );
};

const Grain: React.FC<{amount: number}> = ({amount}) => {
  const frame = useCurrentFrame();
  const ox = Math.floor(random(`gx${frame}`) * 540), oy = Math.floor(random(`gy${frame}`) * 960);
  return <AbsoluteFill style={{backgroundImage: `url(${staticFile('img/grain.png')})`, backgroundSize: '1080px 1920px', backgroundPosition: `${ox}px ${oy}px`,
    mixBlendMode: 'overlay', opacity: amount, pointerEvents: 'none'}} />;
};

const Vignette: React.FC<{strength?: number}> = ({strength = 0.72}) => (
  <AbsoluteFill style={{background: `radial-gradient(ellipse 85% 70% at 50% 46%, rgba(0,0,0,0) 48%, rgba(0,0,0,${strength}) 100%)`, pointerEvents: 'none'}} />
);

const Sweep: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const p = ease(Math.min(1, frame / dur));
  return (
    <AbsoluteFill style={{mixBlendMode: 'screen', pointerEvents: 'none', opacity: 0.55 * Math.sin(Math.PI * p)}}>
      <div style={{position: 'absolute', top: -200, bottom: -200, width: 340, left: -400 + p * (W + 800), transform: 'rotate(18deg)',
        background: 'linear-gradient(90deg, rgba(255,255,255,0), rgba(255,244,214,0.20), rgba(255,255,255,0))', filter: 'blur(18px)'}} />
    </AbsoluteFill>
  );
};

// ---------- a camera shot ----------
const Shot: React.FC<{d: ShotDef}> = ({d}) => {
  const frame = useCurrentFrame();
  const dur = f(d.to - d.from);
  const p = ease(Math.min(1, frame / dur));
  const fadeIn = interpolate(frame, [0, f(0.28)], [0, 1], {extrapolateRight: 'clamp'});
  const fadeOut = interpolate(frame, [dur - f(0.1), dur], [1, 0], {extrapolateLeft: 'clamp'});
  const [ox, oy] = d.cam.o ?? [50, 50];
  const analog = d.grade === 'analog';
  const weave = analog ? Math.sin(frame * 1.7) * 2.2 + (random(`w${frame}`) - 0.5) * 3 : 0;
  const flicker = analog ? 1 - 0.06 * random(`fl${Math.floor(frame / 2)}`) : 1;
  const filt = analog ? 'sepia(0.55) contrast(1.15) saturate(0.75) brightness(0.95)' : 'contrast(1.1) saturate(0.9) brightness(0.96)';
  return (
    <AbsoluteFill style={{opacity: fadeIn * (d.id === 'none' ? 1 : 1) * flicker, backgroundColor: '#000'}}>
      {Math.min(d.cam.s[0], d.cam.s[1]) < 1 ? <Img src={staticFile(`img/${d.img}.png`)} style={{position: 'absolute', width: W, height: H, objectFit: 'cover', filter: 'blur(38px) brightness(0.4)', transform: 'scale(1.25)'}} /> : null}
      <AbsoluteFill style={{overflow: 'hidden', opacity: Math.min(1, fadeOut + 0.0001)}}>
        <Img src={staticFile(`img/${d.img}.png`)} style={{width: W, height: H, objectFit: 'cover', filter: filt,
          transformOrigin: `${ox}% ${oy}%`, transform: `translate(${lerp(p, d.cam.x) + weave}px, ${lerp(p, d.cam.y)}px) scale(${lerp(p, d.cam.s, 1)}) rotate(${lerp(p, d.cam.r)}deg)`}} />
      </AbsoluteFill>
      {d.dust ? <Dust n={d.dust} seed={d.id} /> : null}
      {d.sweep ? <Sweep dur={dur} /> : null}
      <AbsoluteFill style={{background: `linear-gradient(180deg, ${NAVY}cc 0%, ${NAVY}00 38%, ${NAVY}00 62%, ${NAVY}d0 100%)`, pointerEvents: 'none'}} />
      <Vignette />
      {analog ? <Grain amount={0.42} /> : null}
    </AbsoluteFill>
  );
};

// ---------- Seamaster descends through the water into the next shot's pose ----------
const Descent: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const p = ease(Math.min(1, frame / dur));
  const a = interpolate(frame, [0, 18, dur - 6, dur], [0, 1, 1, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{mixBlendMode: 'screen', opacity: a * 0.95, pointerEvents: 'none'}}>
      <Img src={staticFile('img/seamaster.png')} style={{width: W, height: H, objectFit: 'cover', transformOrigin: '50% 50%', filter: 'contrast(1.12)',
        WebkitMaskImage: 'radial-gradient(ellipse 46% 40% at 50% 50%, #000 62%, rgba(0,0,0,0) 100%)', maskImage: 'radial-gradient(ellipse 46% 40% at 50% 50%, #000 62%, rgba(0,0,0,0) 100%)',
        transform: `translateY(${-760 + p * 870}px) scale(0.8) rotate(${-9 + p * 7}deg)`}} />
    </AbsoluteFill>
  );
};

// ---------- typography ----------
const Kicker: React.FC<{from: number; to: number; brand: string; model?: string; y?: number}> = ({from, to, brand, model, y = 1120}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const a = interpolate(t, [from, from + 0.6, to - 0.5, to], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const line = interpolate(t, [from, from + 0.9], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  return (
    <AbsoluteFill style={{alignItems: 'center', opacity: a, pointerEvents: 'none'}}>
      <div style={{position: 'absolute', top: y, textAlign: 'center', transform: `translateY(${(1 - a) * 14}px)`}}>
        <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 28, letterSpacing: '0.55em', color: GOLD, paddingLeft: '0.55em'}}>{brand}</div>
        <div style={{margin: '16px auto', height: 2, width: 220 * line, background: GOLD, opacity: 0.8}} />
        {model ? <div style={{fontFamily: SANS, fontWeight: 300, fontSize: 46, letterSpacing: '0.2em', color: '#F4F1EA', paddingLeft: '0.2em', textShadow: '0 2px 18px rgba(0,0,0,0.7)'}}>{model}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

const Numeral: React.FC<{from: number; to: number; text: string; size?: number; y?: number; flash?: boolean}> = ({from, to, text, size = 380, y = 520}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const reveal = interpolate(t, [from, from + 1.1], [100, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const out = interpolate(t, [to - 0.5, to], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const drift = interpolate(t, [from, to], [0, -26]);
  return (
    <AbsoluteFill style={{opacity: out, pointerEvents: 'none'}}>
      <div style={{position: 'absolute', top: y + drift, left: 0, width: W, textAlign: 'center', clipPath: `inset(0 ${reveal}% 0 0)`,
        fontFamily: SANS, fontWeight: 200, fontSize: size, letterSpacing: '0.04em', lineHeight: 1, color: '#F4F1EA', textShadow: '0 6px 50px rgba(0,0,0,0.8)'}}>{text}</div>
      <div style={{position: 'absolute', top: y + size * 1.02 + drift, left: (W - 460) / 2, height: 3, width: 460 * (1 - reveal / 100), background: GOLD}} />
    </AbsoluteFill>
  );
};

const Disclaimer: React.FC = () => (
  <div style={{position: 'absolute', top: 292, width: W, textAlign: 'center', fontFamily: SANS, fontWeight: 500, fontSize: 24, letterSpacing: '0.3em', color: '#F4F1EA', opacity: 0.62}}>
    VISUALES CONCEPTUALES GENERADOS CON IA
  </div>
);

// ---------- subtitles (safe zone: 270px top / ~480px bottom / 64px sides) ----------
type Chunk = {start: number; end: number; words: {t: string; hi: boolean}[]};
const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const c = (subs as Chunk[]).find((x) => t >= x.start && t < x.end + 0.04);
  if (!c) return null;
  const inP = Math.min(1, (t - c.start) / 0.18);
  const outP = Math.min(1, (c.end - t) / 0.12);
  const a = Math.max(0, Math.min(inP, outP, 1));
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 380, height: 300, opacity: a, background: 'linear-gradient(180deg, rgba(2,5,14,0) 0%, rgba(2,5,14,0.62) 55%, rgba(2,5,14,0) 100%)'}} />
      <div style={{position: 'absolute', bottom: 480, left: 64, right: 64, textAlign: 'center', opacity: a, transform: `translateY(${(1 - inP) * 10}px)`,
        fontFamily: SANS, fontWeight: 600, fontSize: 56, lineHeight: 1.2, letterSpacing: '0.04em', textTransform: 'uppercase', color: '#F4F1EA',
        textShadow: '0 2px 4px rgba(0,0,0,0.9), 0 0 26px rgba(0,0,0,0.85)'}}>
        {c.words.map((w, i) => <React.Fragment key={i}><span style={{color: w.hi ? GOLD : undefined, whiteSpace: 'nowrap'}}>{w.t.toUpperCase()}</span>{i < c.words.length - 1 ? ' ' : ''}</React.Fragment>)}
      </div>
    </AbsoluteFill>
  );
};

// ---------- Reverso flip card: shows the case turning only (no internal mechanism depicted) ----------
const FlipCard: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS + FLIP.from;
  const dur = FLIP.to - FLIP.from;
  const rot = interpolate(t, [FLIP.flipAt, FLIP.flipAt + 0.9, FLIP.flipBackAt, FLIP.flipBackAt + 0.9], [0, 180, 180, 360], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const a = interpolate(t, [FLIP.from, FLIP.from + 0.35, FLIP.to - 0.2, FLIP.to], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const push = interpolate(frame, [0, f(dur)], [1.0, 1.08]);
  const face: React.CSSProperties = {position: 'absolute', inset: 0, backfaceVisibility: 'hidden', borderRadius: 18, overflow: 'hidden'};
  return (
    <AbsoluteFill style={{opacity: a, perspective: 1900, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{width: 600, height: 1067, marginTop: 120, position: 'relative', transformStyle: 'preserve-3d', transform: `scale(${push}) rotateY(${rot}deg)`, boxShadow: '0 60px 120px rgba(0,0,0,0.7)'}}>
        <div style={face}><Img src={staticFile('img/reverso.png')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(1.08) saturate(0.95)'}} /></div>
        <div style={{...face, transform: 'rotateY(180deg)', background: 'linear-gradient(115deg,#2a2e35 0%,#8d949e 22%,#3a3f47 38%,#b7bcc4 55%,#444a53 72%,#20242a 100%)'}}>
          <div style={{position: 'absolute', inset: 36, border: '1px solid rgba(255,255,255,0.18)', borderRadius: 10}} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- finale: three candidates in ONE composition, lit one at a time ----------
// Columns (360 x 650) at y=640. Light cues follow the narration: reveal each watch, then highlight "Omega" / "Jaeger-LeCoultre".
const Column: React.FC<{img: string; c: [number, number]; s: number; x: number; levels: [number, number][]; label: string; sub: string}> = ({img, c, s, x, levels, label, sub}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS + FINALE.from;
  const lit = interpolate(t, levels.map((l) => l[0]), levels.map((l) => l[1]), {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const cx = (c[0] / 100) * W, cy = (c[1] / 100) * H;
  const drift = Math.sin((t - FINALE.from) * 0.8) * 6;
  return (
    <div style={{position: 'absolute', left: x, top: 540, width: 360, height: 760, overflow: 'hidden'}}>
      <Img src={staticFile(`img/${img}.png`)} style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0',
        transform: `translate(${180 - cx * s}px, ${380 - cy * s + drift}px) scale(${s})`,
        filter: `brightness(${0.1 + 0.9 * lit}) saturate(${0.4 + 0.6 * lit}) contrast(1.08)`}} />
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse 85% 70% at 50% 46%, rgba(0,0,0,0) ${20 + 40 * lit}%, rgba(0,0,0,${0.85 - 0.35 * lit}) 100%)`}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 22, textAlign: 'center', opacity: 0.25 + 0.75 * lit, fontFamily: SANS}}>
        <div style={{fontWeight: 600, fontSize: 17, letterSpacing: '0.3em', color: GOLD, paddingLeft: '0.3em'}}>{label}</div>
        <div style={{fontWeight: 300, fontSize: 21, letterSpacing: '0.14em', color: '#F4F1EA', marginTop: 4, paddingLeft: '0.14em'}}>{sub}</div>
      </div>
    </div>
  );
};

const Finale: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS + FINALE.from;
  const fade = interpolate(frame, [0, f(0.5)], [0, 1], {extrapolateRight: 'clamp'});
  const q = interpolate(t, [63.9, 64.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const mark = interpolate(t, [68.5, 69.4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tag = interpolate(t, [60.4, 61.1, 63.6, 64.2], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // reveal one by one (60.9 / 62.2 / 63.4), then highlight Omega (66.2) vs Jaeger-LeCoultre (67.1)
  const omega: [number, number][] = [[60.9, 0], [62.0, 1], [65.9, 1], [66.4, 1], [67.0, 0.45]];
  const polaris: [number, number][] = [[61.9, 0], [63.0, 1], [66.2, 1], [66.6, 0.5], [67.2, 1]];
  const reverso: [number, number][] = [[63.1, 0], [64.1, 1], [66.2, 1], [66.6, 0.5], [67.3, 1]];
  const lv = (a: [number, number][]) => a.map((p) => [p[0], p[1]] as [number, number]);
  return (
    <AbsoluteFill style={{backgroundColor: '#03060F', opacity: fade}}>
      <Column img="seamaster" c={[50, 49]} s={0.52} x={0} levels={lv(omega)} label="OMEGA" sub="SEAMASTER" />
      <Column img="polaris" c={[48, 45]} s={0.52} x={360} levels={lv(polaris)} label="JAEGER-LECOULTRE" sub="POLARIS" />
      <Column img="reverso" c={[50, 48]} s={0.5} x={720} levels={lv(reverso)} label="JAEGER-LECOULTRE" sub="REVERSO" />
      {[360, 720].map((x) => <div key={x} style={{position: 'absolute', top: 540, height: 760, left: x - 1, width: 2, background: `linear-gradient(180deg, transparent, ${GOLD}, transparent)`, opacity: 0.6}} />)}
      <Dust n={26} seed="fin" />
      <AbsoluteFill style={{background: `linear-gradient(180deg, ${NAVY}00 0%, ${NAVY}00 70%, ${NAVY}cc 100%)`}} />
      <div style={{position: 'absolute', top: 360, width: W, textAlign: 'center', opacity: tag, fontFamily: SANS, fontWeight: 600, fontSize: 24, letterSpacing: '0.4em', color: GOLD, paddingLeft: '0.4em'}}>HIPÓTESIS EDITORIAL · NADA CONFIRMADO</div>
      <div style={{position: 'absolute', top: 340, left: 0, width: W, textAlign: 'center', opacity: q, transform: `translateY(${(1 - q) * 18}px)`,
        fontFamily: SANS, fontWeight: 500, fontSize: 70, letterSpacing: '0.1em', color: '#F4F1EA', lineHeight: 1.14, textShadow: '0 4px 40px rgba(0,0,0,0.95), 0 0 12px rgba(0,0,0,0.9)'}}>
        ¿OMEGA O<br /><span style={{color: GOLD}}>JAEGER-LECOULTRE</span>?
      </div>
      <div style={{position: 'absolute', top: 1330, width: W, textAlign: 'center', opacity: mark, fontFamily: SANS}}>
        <div style={{margin: '0 auto 18px', width: 80, height: 2, background: GOLD}} />
        <div style={{fontWeight: 300, fontSize: 42, letterSpacing: '0.62em', color: '#F4F1EA', paddingLeft: '0.62em'}}>ALARION</div>
        <div style={{fontWeight: 500, fontSize: 20, letterSpacing: '0.7em', color: GOLD, paddingLeft: '0.7em', marginTop: 10}}>WATCHES</div>
      </div>
      <Vignette strength={0.5} />
    </AbsoluteFill>
  );
};

// ---------- main ----------
export const Main: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {SHOTS.map((d) => (
        <Sequence key={d.id} from={f(d.from)} durationInFrames={f(d.to - d.from) + 2}><Shot d={d} /></Sequence>
      ))}
      <Sequence from={f(FLIP.from)} durationInFrames={f(FLIP.to - FLIP.from)}>
        <AbsoluteFill style={{backgroundColor: '#000'}}>
          <Img src={staticFile('img/city.png')} style={{width: W, height: H, objectFit: 'cover', filter: 'blur(14px) brightness(0.55)', transform: 'scale(1.15)'}} />
          <Dust n={22} seed="flip" /><Vignette /><FlipCard />
        </AbsoluteFill>
      </Sequence>
      <Sequence from={f(24.9)} durationInFrames={f(2.4)}><Descent dur={f(2.2)} /></Sequence>
      <Sequence from={f(FINALE.from)} durationInFrames={f(FINALE.to - FINALE.from)}><Finale /></Sequence>

      {/* typography beats, aligned to the narration */}
      <Kicker from={0.3} to={3.0} brand="ROBERT PATTINSON" y={385} />
      <Numeral from={3.1} to={6.2} text="007" size={430} y={560} />
      <Numeral from={9.5} to={12.7} text="1995" size={320} y={620} />
      <Kicker from={27.1} to={30.1} brand="OMEGA" model="SEAMASTER DIVER 300M" y={385} />
      <Kicker from={37.6} to={40.2} brand="JAEGER-LECOULTRE" model="POLARIS" y={385} />
      <Kicker from={46.9} to={50.0} brand="JAEGER-LECOULTRE" model="REVERSO" y={385} />
      <Numeral from={55.6} to={58.4} text="1962" size={320} y={640} />
      <Kicker from={58.5} to={60.3} brand="ROLEX" model="SUBMARINER" y={385} />

      <Subtitles />
      <Sequence from={0} durationInFrames={f(TOTAL_SECONDS)}><Disclaimer /></Sequence>
      <Grain amount={0.1} />
      <Audio src={staticFile('audio/mix.mp3')} />
    </AbsoluteFill>
  );
};
