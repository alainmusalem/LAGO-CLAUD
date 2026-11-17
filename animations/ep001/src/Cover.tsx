import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {GOLD, NAVY} from './timeline';

const SANS = '"Inter Display","Inter",sans-serif';

// Social cover (1080x1920): everything important sits inside the Reels/TikTok safe area (y 270..1500).
export const Cover: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: '#000'}}>
    <Img src={staticFile('img/desk.png')} style={{width: 1080, height: 1920, objectFit: 'cover', filter: 'contrast(1.1) saturate(0.9) brightness(0.9)', transform: 'scale(1.12)', transformOrigin: '40% 55%'}} />
    <AbsoluteFill style={{background: `linear-gradient(180deg, ${NAVY}d0 0%, ${NAVY}00 40%, ${NAVY}00 55%, ${NAVY}e6 100%)`}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 85% 70% at 50% 46%, rgba(0,0,0,0) 48%, rgba(0,0,0,0.7) 100%)'}} />
    <div style={{position: 'absolute', top: 330, width: 1080, textAlign: 'center', fontFamily: SANS, fontWeight: 200, fontSize: 470, lineHeight: 1, color: '#F4F1EA', letterSpacing: '0.04em', textShadow: '0 6px 60px rgba(0,0,0,0.85)'}}>007</div>
    <div style={{position: 'absolute', top: 820, left: (1080 - 460) / 2, width: 460, height: 3, background: GOLD}} />
    <div style={{position: 'absolute', top: 900, width: 1080, textAlign: 'center', fontFamily: SANS, fontWeight: 500, fontSize: 68, letterSpacing: '0.09em', lineHeight: 1.18, color: '#F4F1EA', textShadow: '0 4px 40px rgba(0,0,0,0.95)'}}>
      ¿QUÉ RELOJ<br />UTILIZARÁ EL NUEVO<br /><span style={{color: GOLD}}>JAMES BOND</span>?
    </div>
    <div style={{position: 'absolute', top: 1320, width: 1080, textAlign: 'center', fontFamily: SANS}}>
      <div style={{fontWeight: 300, fontSize: 38, letterSpacing: '0.62em', color: '#F4F1EA', paddingLeft: '0.62em'}}>ALARION</div>
      <div style={{fontWeight: 500, fontSize: 20, letterSpacing: '0.7em', color: GOLD, paddingLeft: '0.7em', marginTop: 8}}>WATCHES</div>
    </div>
  </AbsoluteFill>
);
