# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_state.c

Read completely: 73 lines.

This file provides the non-threaded global resolver state `_nres` and accessors `__res_get_state_nothread` and `__res_put_state_nothread`, with weak aliases for `__res_get_state`, `__res_put_state`, and source-compatible `__res_state`.

Key behavior: on first access, it calls `res_ninit(&_nres)` and returns `NULL` with `h_errno = NETDB_INTERNAL` if initialization fails. `__res_put_state_nothread` is a no-op.

Important interactions: used by non-reentrant resolver wrappers and compatibility code; threaded builds can override these weak aliases with thread-local resolver state.

Security/reliability notes: `_nres` is shared process-global state and unsuitable for concurrent mutation without the threaded resolver layer.
