# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_null.c

## Purpose
Implements the NFS NULL procedure for all protocol versions. NULL is a liveness/no-op RPC that returns success without inspecting inputs.

## Important APIs, Types, and Functions
- `nfs_null` logs request processing and returns `NFS3_OK`.
- `nfs_null_free` is a no-op result cleanup hook.

## Control Flow
`nfs_null` ignores `arg`, `req`, and `res`, emits a debug log on `COMPONENT_NFSPROTO`, and returns success. The free hook does nothing.

## State and Persistence Behavior
No state is read or mutated beyond logging.

## Dependencies and Integration Points
Integrated as the NULL procedure entry point in the NFS RPC dispatch table. Includes common NFS headers for shared types, but does not call NFSv4-specific machinery.

## Risks
Minimal. The return value uses `NFS3_OK`, which is numerically appropriate for NULL success across versions but can be confusing to readers.

## Test Signals
Test that NULL succeeds for supported NFS program versions, ignores malformed/empty arguments, does not allocate response resources, and can be used as a cheap server liveness probe.
