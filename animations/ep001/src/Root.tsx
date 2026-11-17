import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {Cover} from './Cover';
import {FPS, TOTAL_SECONDS} from './timeline';

export const Root: React.FC = () => (
  <>
    <Composition id="Cover" component={Cover} width={1080} height={1920} fps={FPS} durationInFrames={1} />
    <Composition id="Main" component={Main} width={1080} height={1920} fps={FPS}
      durationInFrames={Math.round(TOTAL_SECONDS * FPS)} />
  </>
);
