# File Research: sources/os/bsd/dragonflybsd/sys/sys/sfbuf.h

This kernel-only header defines sendfile/lightweight page buffer wrappers around DragonFly `lwbuf`.

Key responsibilities:
- Includes `<cpu/lwbuf.h>`.
- Rejects userland inclusion unless kernel structures are requested.
- Defines `struct sf_buf`:
  - pointer to active `lwbuf`
  - reference count
  - cached embedded `lwbuf`
- Defines access macros:
  - `sf_buf_kva()`
  - `sf_buf_page()`
- Declares kernel APIs:
  - `sf_buf_alloc()`
  - `sf_buf_ref()`
  - `sf_buf_free()`

Important invariants:
- `sf_buf_kva()` and `sf_buf_page()` delegate directly to the active `lwbuf`.
- The structure supports reference counting for page mappings used by sendfile-style paths.

Research notes:
- This is a small compatibility/abstraction layer over DragonFly lightweight buffers.
