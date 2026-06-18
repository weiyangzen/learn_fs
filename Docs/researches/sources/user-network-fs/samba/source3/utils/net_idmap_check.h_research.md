# sources/user-network-fs/samba/source3/utils/net_idmap_check.h

## Purpose
This header defines the small public contract for the idmap database checker used by `net idmap check`.

## Important APIs, Types, And Control Flow
It forward-declares `struct net_context`, defines `struct check_options`, and declares `int net_idmap_check_db(const char *db, const struct check_options *opts)`. The options control dry-run behavior, verbosity, transaction locking, automatic prompt answers, forced repair/commit behavior, and whether repair mode is enabled.

## State And Persistence
The header itself stores no state. Its option fields control whether `net_idmap_check.c` opens the target TDB read-only or writable, stages and commits repairs, or cancels transactions in test mode.

## Dependencies And Integration Points
It includes only `<stdbool.h>` and is consumed by `net_idmap.c` and implemented by `net_idmap_check.c`. It intentionally exposes no checker internals such as record parsing or diff storage.

## Risks And Test Signals
The type name `struct check_options` is generic and duplicated by the registry checker header, so callers must avoid including both incompatible headers in one translation unit. Test signals are compile coverage for the declaration and option mapping tests from `net_idmap.c` flags into the checker.
