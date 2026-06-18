# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/store.h

Assignment and constructor macros for Ghostscript interpreter `ref` objects.

Key points:
- Includes `ialloc.h` and `idosave.h`.
- Defines `ref_assign` and `ref_assign_inline`, with old compiler-specific tuning.
- Implements save/restore-aware assignment:
  - `ref_must_save*`
  - `ref_do_save*`
  - `ref_save*`
  - `ref_mark_new*`
  - `ref_assign_new*`
  - `ref_assign_old*`
- Provides debug fill patterns for partially initialized refs under `DEBUG`.
- Defines generic constructors:
  - `make_t`, `make_ta`
  - `make_tv`
  - `make_tav`
  - `make_tasv`
- Defines type-specific constructors for booleans, integers, marks, nulls, operators, reals, arrays, strings, structs, and array-structs.
- Distinguishes stack stores, new-object stores, and old-object stores that require save tracking.

Dependencies and interactions:
- Relies on interpreter memory masks from `idmemory`/`gs_ref_memory_t`.
- Used throughout interpreter code when writing refs into VM-managed composite objects.

Research relevance:
- Central correctness layer for PostScript VM save/restore and local/global allocation tracking.
