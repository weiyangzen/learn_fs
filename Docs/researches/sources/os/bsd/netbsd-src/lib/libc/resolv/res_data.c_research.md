# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_data.c

Compatibility wrapper layer exposing traditional resolver APIs over the stateful `res_n*` interfaces and global `_nres`.

Key behavior:
- `res_init()` initializes `_nres`, preserving direct `_res` compatibility fields under `COMPAT__RES`, setting defaults for retrans/retry/options/id, and calling `__res_vinit()`.
- Query/send/update wrappers lazily call `res_init()` if needed, set `NETDB_INTERNAL` on init failure where appropriate, then delegate to `res_nmkquery()`, `res_nquery()`, `res_nsend()`, `res_nsearch()`, `res_nquerydomain()`, etc.
- Debug wrappers route `p_query()`, `fp_query()`, and `fp_nquery()` through `res_pquery()`.
- Hook setters write `_nres.qhook` and `_nres.rhook`.
- Miscellaneous wrappers include `res_close()`, `res_isourserver()`, `res_opt()`, `res_randomid()`, and `hostalias()`.

This file is the main old-API facade over modern resolver state management.
