<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h

## Purpose

`nfsdcltrack/sqlite.h` declares the SQLite API for the older `nfsdcltrack` helper.

## Important APIs, types, and functions

It declares preparation, client insert/remove/check, removal of unreclaimed clients by grace time, and query for still-reclaiming clients.

## Control flow

No executable flow exists. Command handlers prepare the database first, then call the appropriate operation for create/remove/check/gracedone/init.

## State and persistence behavior

The declared functions operate on a process-global sqlite handle and persistent `clients` table in the configured storage directory.

## Dependencies and integration points

The header is included by `nfsdcltrack.c` and its SQLite implementation. It uses `bool`, `size_t`, `uint64_t`, and `time_t`, so including translation units must provide the relevant standard headers before or through their include chain.

## Risks and edge cases

The API does not expose a shutdown call; short-lived helper process exit closes resources. Return-code conventions require callers to translate sqlite failures into kernel-facing errors.

## Test signals

Compile tests should verify required type visibility. API tests should cover check behavior with `has_session` true and false and grace-time pruning.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h -->
