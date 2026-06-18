<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h

## Purpose

`nfsdcld/sqlite.h` declares the SQLite backend interface for the client-tracking daemon.

## Important APIs, types, and functions

It forward-declares `struct cld_client` and declares database preparation, client insert/remove/check, insert with Kerberos principal hash, grace start/done, recovery iteration callback, old cltrack cleanup, first-time completion, and shutdown.

## Control flow

No executable flow exists. The intended sequence is prepare database at daemon startup, service create/remove/check/grace commands, optionally iterate recovery clients during `Cld_GraceStart`, then shut down.

## State and persistence behavior

The declared functions operate on a process-global sqlite handle and epoch globals. Persistent state is in `main.sqlite`.

## Dependencies and integration points

The header is included by `nfsdcld.c`, `legacy.c`, and `sqlite.c`. It abstracts SQL details away from pipe command handling.

## Risks and edge cases

Return values mix negative errno-style errors and sqlite result codes depending on function, so callers must preserve existing mapping behavior. The callback form of `sqlite_iterate_recovery` mutates the supplied client message buffer.

## Test signals

API tests should validate return-code mapping and callback behavior for recovery iteration, including empty and multi-record recovery tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h -->
