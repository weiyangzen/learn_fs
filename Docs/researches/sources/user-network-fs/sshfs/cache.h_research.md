# sources/user-network-fs/sshfs/cache.h

Purpose: header declaring the sshfs FUSE cache wrapper API.

Important APIs/types/functions: `cache_wrap`, `cache_parse_options`, `cache_add_attr`, `cache_invalidate`, and `cache_get_write_ctr`.

Control flow: no implementation; it exposes cache lifecycle, option parsing, explicit invalidation, and write-counter access to `sshfs.c`.

State and persistence behavior: declarations only; state lives in `cache.c`.

Dependencies and integration points: includes FUSE headers and is included by `sshfs.c` and `cache.c`.

Risks: public functions expose raw paths and stat pointers; callers must follow locking/ordering expectations documented only by implementation.

Test signals: compile-time integration and behavior tests through `cache.c`/sshfs with `dir_cache` options.
