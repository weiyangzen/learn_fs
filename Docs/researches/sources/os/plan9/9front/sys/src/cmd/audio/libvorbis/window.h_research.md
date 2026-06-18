# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.h

Small private header for libvorbis window helpers.

Important contents:
- Include guard `_V_WINDOW_`.
- Declares `extern const float *_vorbis_window_get(int n);`.
- Declares `extern void _vorbis_apply_window(float *d,int *winno,long *blocksizes,int lW,int W,int nW);`.

Integration points:
- Included by `window.c`.
- Used by other libvorbis internals needing access to precomputed window coefficients or direct window application.

Risk and review signals:
- No implementation in this file.
- Function contracts are implicit; callers must know legal window indexes, block sizes, and Vorbis lapping semantics from codec internals.

Filesystem relevance:
- No filesystem logic. This is a private audio codec header.
