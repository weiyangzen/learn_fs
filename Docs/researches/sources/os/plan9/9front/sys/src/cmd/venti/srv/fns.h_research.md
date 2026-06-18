# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fns.h

Central prototype header for the Venti server storage subsystem.

Key contents:
- Declares arena, arena partition, arena summary, index, index-section, cache, Bloom, clump, config, HTTP, stats, formatting, I/O, and utility functions.
- Exposes low-level disk functions `readpart`, `writepart`, `flushpart`, `initpart`, and block cache operations.
- Exposes index cache operations `icachelookup`, `insertscore`, `icachedirty`, `icacheclean`, and background flush controls.
- Declares pack/unpack conversion routines from `conv.c`.
- Declares command-support helpers such as `printarena`, `printindex`, and `ventifmtinstall`.
- Defines convenience macros `scorecmp`, `scorecp`, and allocation wrappers `MK`, `MKZ`, `MKN`, `MKNZ`, `MKNA`.

Notable details:
- `clumpinfoeq` is declared twice.
- Comment on `readpart`: return value is success byte count unless negative, but asking for `n == -1` always reports failure.
