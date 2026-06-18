# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/export.c

## Purpose
Implements PSEUDO FSAL export creation, release, static dynamic info, unsupported quota ops, wire-handle endian normalization, and export-op vector wiring.

## Important APIs, Types, and Functions
Functions: `release`, `get_dynamic_info`, `get_quota`, `set_quota`, `wire_to_host`, `pseudofs_export_ops_init`, and `pseudofs_create_export`.

## Control Flow
Export creation allocates `pseudofs_fsal_export`, initializes FSAL export state, installs ops, attaches to the FSAL, records `CTX_FULLPATH(op_ctx)`, and sets `op_ctx->fsal_export`. Release frees root handle/path/export resources. `wire_to_host` byte-swaps hash and length fields when flags indicate opposite endian.

## State and Persistence Behavior
Runtime state is in-memory export path plus root handle pointer. Dynamic info returns zeros and default time delta. Quotas are unsupported.

## Dependencies and Integration Points
Depends on FSAL common/config, export manager context, mdcache, and PSEUDO handle functions.

## Risks
`wire_to_host` checks only a one-byte minimum before reading larger fields. Release handles root directly; child lifetime depends on unlink/handle release paths. Capacity/quota data are placeholders.

## Test Signals
Pseudo export creation/release, root lookup, endian handle decode, and `ERR_FSAL_NOTSUPP` quota responses.
