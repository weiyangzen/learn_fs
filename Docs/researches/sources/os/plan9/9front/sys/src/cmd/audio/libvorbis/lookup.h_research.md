# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.h

Declaration header for optional lookup-table math helpers.

Important contents:
- Declares float lookup helpers when `FLOAT_LOOKUP` is defined.
- Declares integer lookup helpers when `INT_LOOKUP` is defined.

Integration points:
- Included by `lookup.c` and `lsp.c`.

Risk and review signals:
- The header has `#ifndef _V_LOOKUP_H_` but does not define `_V_LOOKUP_H_`, so it does not actually prevent repeated inclusion.
- No implementation is present; available declarations depend entirely on compile-time lookup mode macros.

Filesystem relevance:
- No filesystem logic.
