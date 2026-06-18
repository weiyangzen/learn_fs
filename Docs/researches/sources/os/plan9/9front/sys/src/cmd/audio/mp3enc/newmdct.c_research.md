# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.c

## Scope
Layer III subband analysis, MDCT transform, filtering, and alias-reduction implementation.

## Data and Algorithms
Defines analysis window constants, MDCT windows for normal/start/short/stop block types, short-block trig tables, alias reduction constants, and subband output ordering. `window_subband()` applies the overlapping analysis window and fast cosine-style reduction. `mdct_short()` transforms three short windows. `mdct_long()` transforms long blocks. `mdct_sub48()` drives 48 subband samples per granule/channel, applies highpass/lowpass transition-band gains, chooses block type including mixed-block handling, zeros filtered bands, performs MDCT, and applies alias-reduction butterflies for non-short blocks.

## Dependencies
Includes `util.h`, `l3side.h`, and `newmdct.h`; uses LAME internal fields such as `l3_side`, `sb_sample`, `channels_out`, `mode_gr`, filter bands, and amplitude tables.

## Risks and Notes
Performance-critical, table-heavy DSP code with pointer arithmetic and negative indexes relative to working buffers. Correctness depends on upstream buffer layout and constants such as `SBLIMIT`, `SHORT_TYPE`, and block-type definitions.
