<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h

## Purpose

`cld-internal.h` defines private shared state for the `nfsdcld` daemon and SQLite backend.

## Important APIs, types, and functions

It computes `UPCALL_VERSION` from `CLD_UPCALL_VERSION`. `struct cld_client` stores the cld pipe fd, libevent event pointer, and a union of v1/v2 kernel message formats. It declares global `current_epoch`, `recovery_epoch`, `first_time`, `num_cltrack_records`, and `num_legacy_records`.

## Control flow

No executable flow exists. The data layout lets the event-loop code read either upcall format and lets `sqlite.c` update epoch globals.

## State and persistence behavior

The declared globals mirror SQLite database state and first-time migration status during daemon runtime. Persistent copies live in the SQLite `grace` and `parameters` tables.

## Dependencies and integration points

It depends on `cld.h` message definitions and libevent's `struct event` being visible through including translation units. It is shared by `nfsdcld.c` and `sqlite.c`.

## Risks and edge cases

The message union must stay large enough and aligned for all supported kernel upcall versions. Globals make only one active database/daemon context practical per process.

## Test signals

Compile tests should cover builds with upcall v1 and v2. Runtime tests should verify v1/v2 message sizing and epoch global updates after database startup and grace transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h -->
