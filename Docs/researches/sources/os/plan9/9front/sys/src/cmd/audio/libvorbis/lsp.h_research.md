# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.h

Declaration header for LSP/LSF conversion routines.

Important contents:
- Declares `vorbis_lpc_to_lsp()`.
- Declares `vorbis_lsp_to_curve()`.

Integration points:
- Used by `lsp.c` and `floor0.c`.

Risk and review signals:
- Header only; callers must account for `vorbis_lsp_to_curve()` modifying the LSP input buffer.

Filesystem relevance:
- No filesystem logic.
