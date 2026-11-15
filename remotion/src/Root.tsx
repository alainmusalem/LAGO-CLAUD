import React from 'react';
import {Composition, OffthreadVideo, Sequence, staticFile} from 'remotion';

// Reads the same EDL JSON produced by `python -m lago edit`. Cuts only: no overlays, no effects.
type Seg = {start: number; end: number};
type Props = {src: string; fps: number; segments: Seg[]; cropX: number; srcW: number; srcH: number};

const defaults: Props = {src: 'source.mp4', fps: 30, segments: [{start: 0, end: 1}], cropX: 0.5, srcW: 1920, srcH: 1080};

const Edit: React.FC<Props> = ({src, fps, segments, cropX, srcW, srcH}) => {
  let cursor = 0;
  // Fill 1080x1920 by scaling to cover, then position the horizontal crop window with cropX (0..1).
  const scale = Math.max(1080 / srcW, 1920 / srcH);
  const w = srcW * scale, h = srcH * scale;
  const left = -(w - 1080) * cropX;
  return (
    <>
      {segments.map((s, i) => {
        const from = cursor;
        const dur = Math.max(1, Math.round((s.end - s.start) * fps));
        cursor += dur;
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <OffthreadVideo src={staticFile(src)} startFrom={Math.round(s.start * fps)}
              style={{position: 'absolute', width: w, height: h, left, top: 0}} />
          </Sequence>
        );
      })}
    </>
  );
};

export const Root: React.FC = () => (
  <Composition id="Edit" component={Edit} width={1080} height={1920} fps={defaults.fps}
    durationInFrames={300} defaultProps={defaults}
    calculateMetadata={({props}) => ({
      fps: props.fps,
      durationInFrames: Math.max(1, props.segments.reduce((a, s) => a + Math.round((s.end - s.start) * props.fps), 0)),
    })} />
);
