# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar42.h

This header declares the shared Type 42 cache setup helper.

Key content:
- Include guard `zchar42_INCLUDED`.
- Declares `zchar42_set_cache(i_ctx_t *, gs_font_base *, ref *, uint glyph_index, op_proc_t cont, op_proc_t *exec_cont, bool put_lsb)`.

Used by:
- `zchar.c` for CID TrueType CDevProc/cache paths.
- `zchar42.c` as the implementation file.

Research notes:
- The header is narrow and only exposes one cross-file Type 42 helper.
