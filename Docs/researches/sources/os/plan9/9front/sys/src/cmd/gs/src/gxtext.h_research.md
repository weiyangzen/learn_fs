# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtext.h

Internal support header for Ghostscript device text enumeration.

Key contents:
- Defines `gs_text_returned_t` for client-visible current character, current glyph, and accumulated width.
- Defines composite-font stack structures, including modal and non-modal composite font levels up to `MAX_FONT_STACK`.
- Defines `gs_text_enum_common`, the shared layout embedded by all text enumerator implementations.
- Common enumerator state stores text parameters, target devices, imager state, original/current font, path/color/clip pointers, memory, refcount header, font stack, cached font/matrix pair, indices, CMap status, grid-fitting flags, and returned values.
- Documents the `imaging_dev` hack used by forwarding/bbox devices to account for low-level drawing done by another target.
- Declares GC structure descriptor macro `public_st_gs_text_enum`.
- Declares `gs_text_enum_init` and `gs_text_enum_copy_dynamic`.
- Provides `SHOW_IS_*` macros for text operation tests.
- Defines `gs_text_enum_procs_t` callbacks: `resync`, `process`, `is_width_only`, `current_width`, `set_cache`, `retry`, and `release`.
- Declares `gx_default_text_release`.

Dependencies:
- Includes public text definitions from `gstext.h`.
- Includes reference-count support from `gsrefct.h`.

Research notes:
- Text enumeration is refcounted; implementers must release referenced objects through the release callback path.
- The comments state that no fully generic default `process` implementation exists because text processing must handle path construction, intervention returns, width reporting, font restoration, and cache setup.
