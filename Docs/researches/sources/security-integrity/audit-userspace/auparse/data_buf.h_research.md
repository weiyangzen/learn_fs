# sources/security-integrity/audit-userspace/auparse/data_buf.h

Purpose: Declares the `DataBuf` structure and helper API for auparse input buffering.

Important APIs, types, and functions: Defines `DATABUF_FLAG_PRESERVE_HEAD`, `DataBuf` fields (`flags`, `alloc_size`, `alloc_ptr`, `offset`, `len`, `max_len`), inline `databuf_beg()`, and hidden functions for print/init/free/append/replace/advance/reset.

Control flow: Header-only inline `databuf_beg()` returns NULL for unallocated buffers or the logical beginning pointer. Other flow is implemented in `data_buf.c`.

State and persistence: The struct is mutable state embedded in `auparse_state_t`; ownership of `alloc_ptr` belongs to the `DataBuf`.

Dependencies and integration points: Includes `config.h` and `private.h` for build and visibility macros. Used by auparse core input source handling.

Risks and edge cases: External code that manipulates fields directly can violate invariants (`offset + len <= alloc_size`). The preserve-head flag changes append/advance/reset semantics and must match source type.

Test signals: Indirect through auparse buffer and feed parsing; direct tests would validate append/grow/advance/reset invariants.
