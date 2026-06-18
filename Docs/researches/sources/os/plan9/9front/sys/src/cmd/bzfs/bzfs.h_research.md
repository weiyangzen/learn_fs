# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/bzfs.h

This header declares shared entry points for the bzip-backed filesystem utilities.

Contents:
- Decompression pipeline functions: `unbzip`, `_unbzip`, `unbflz`, `xexpand`.
- Allocation helpers: `emalloc`, `erealloc`, `estrdup`.
- RAM filesystem entry point: `ramfsmain`.
- Shared verbosity flag `chatty`.
- Shared fatal reporter `error`.

Notable detail:
- `xexpand` is declared here but not present in the listed files.
