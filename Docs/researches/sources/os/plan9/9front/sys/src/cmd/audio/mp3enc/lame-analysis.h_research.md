# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame-analysis.h

This header defines data captured for LAME's MP3 frame analyzer/plotting support.

Key constants:
- `READ_AHEAD`
- `MAXMPGLAG`
- `NUMBACK`
- `NUMPINFO`

Main structure:
- `plotting_data`: large per-frame analysis snapshot containing PCM data, MDCT data, decoded comparison data, MS ratios, energy, thresholds, scalefactors, quantization metadata, noise metrics, block types, frame header properties, bit counts, and reservoir data.

Export:
- `extern plotting_data *pinfo`

Dependencies:
- Includes `encoder.h` for block sizes and constants.

Integration:
- `encoder.c` writes analysis data into `gfc->pinfo`.
- Intended for GTK plotting/frame-analyzer tooling rather than normal encoding output.

Risks:
- Large structure with many fixed-size arrays.
- Global `pinfo` suggests non-reentrant analyzer state.
