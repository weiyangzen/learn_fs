# sources/security-integrity/audit-userspace/src/libev/ev_select.c

Purpose: implements the `select(2)` backend for libev fd readiness. It is the broadest portability backend and supports either native `fd_set` storage or custom bit-vector storage depending on platform macros.

Important APIs/functions: backend hooks are `select_init`, `select_modify`, `select_poll`, and `select_destroy`. It manages input/output read and write vectors `vec_ri`, `vec_ro`, `vec_wi`, `vec_wo`, optional Windows exception vector `vec_eo`, and `vec_max` for custom bit vectors.

Control flow: `select_modify` updates the persistent interest sets for read and write events, allocating larger bit vectors when not using `fd_set`. `select_poll` copies interest sets to output sets, calls `select` with a computed timeout, handles Windows-specific error behavior, dispatches `EBADF`/`ENOMEM` recovery, and scans resulting sets to feed fd events. `select_init` allocates and zeroes vectors; `select_destroy` frees them.

State and persistence: the backend persists desired read/write sets in memory and creates per-poll copies because `select` mutates them. No kernel registration persists between calls. With custom vectors, `vec_max` grows to cover the highest watched fd word and is not shrunk.

Dependencies and integration: uses `<sys/select.h>`, `<inttypes.h>`, `<string.h>`, and Windows socket compatibility branches through macros supplied by `ev.c`. It is included under `EV_USE_SELECT` and selected last among standard backends.

Risks: fd-set mode is limited by `FD_SETSIZE` and asserts if callers exceed it. Windows requires special handling because `select` operates on sockets and reports some errors in the exception set or as `EINVAL`. Custom bit-vector mode depends on `NFDBITS`/`fd_mask` details. Linear scanning across `anfdmax` or vector words can be expensive for sparse high fds.

Test signals: build both `fd_set` and custom-vector modes where possible, watch fds near `FD_SETSIZE`, exercise read/write readiness and timeout behavior, close watched fds to trigger `EBADF`, and run Windows socket tests if that configuration is supported.
