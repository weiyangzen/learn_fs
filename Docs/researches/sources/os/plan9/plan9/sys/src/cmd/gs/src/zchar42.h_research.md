# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.h

Declares the Type 42 cache setup helper.

Key behavior:
- Provides include guard `zchar42_INCLUDED`.
- Declares `zchar42_set_cache(i_ctx_t *, gs_font_base *, ref *, uint glyph_index, op_proc_t cont, op_proc_t *exec_cont, bool put_lsb)`.

Dependencies and coupling:
- Used by `zchar.c` to set caches for CID TrueType CDevProc paths and by `zchar42.c` as the implementation contract.
