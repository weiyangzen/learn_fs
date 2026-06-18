<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.h -->
# sources/user-network-fs/nfs-utils/utils/mountd/mountd.h

## Purpose

`mountd.h` declares the RPC service handlers and shared helper interfaces used across the `rpc.mountd` implementation.

## Important APIs, types, and functions

It includes RPC, NFS library, exportfs, and mount protocol headers. It defines `union mountd_arguments` and `union mountd_results` for dispatch storage. It declares mount service procedures, `mount_dispatch`, auth hooks, and rmtab list operations.

## Control flow

The header has no executable logic. Its declarations connect `mount_dispatch.c` table entries to `mountd.c` service handlers and `rmtab.c` state functions.

## State and persistence behavior

The header exposes functions that mutate export auth/cache and rmtab state, but it stores no state itself. Callers use the declared rmtab functions to update persistent mount records.

## Dependencies and integration points

It is the internal interface between the dispatch table, daemon implementation, and rmtab persistence module. It also establishes the argument/result union types expected by `rpc_dispatch`.

## Risks and edge cases

Any mismatch between union fields and dispatch table XDR types can corrupt request decoding. Because auth functions are declared here but implemented elsewhere, changes in export authentication contracts must be synchronized.

## Test signals

Build tests should compile all mountd translation units against this header. RPC dispatch tests should validate that each declared service handler matches its expected argument/result type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.h -->
