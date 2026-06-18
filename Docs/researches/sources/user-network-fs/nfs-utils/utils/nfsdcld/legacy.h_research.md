<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h

## Purpose

`legacy.h` declares the legacy recovery-directory migration helpers used by `nfsdcld`.

## Important APIs, types, and functions

It declares `legacy_load_clients_from_recdir(int *)` and `legacy_clear_recdir(void)`.

## Control flow

No executable flow exists. Callers use the load helper during first-time database preparation and the clear helper after first grace completion.

## State and persistence behavior

The declared functions read and remove legacy recovery directory state and may insert records into SQLite through `legacy.c`.

## Dependencies and integration points

It is included by `nfsdcld.c` and `sqlite.c`, connecting daemon grace handling and database initialization to legacy on-disk cleanup.

## Risks and edge cases

The header does not describe ownership or error reporting; the implementation logs and returns mostly through side effects, so callers cannot distinguish many failure classes.

## Test signals

Build tests should ensure both daemon and SQLite modules include the header and agree on the count-pointer contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h -->
