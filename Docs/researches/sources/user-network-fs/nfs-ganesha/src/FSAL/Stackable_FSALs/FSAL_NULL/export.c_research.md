<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c

## Purpose

This file implements NULLFS export-level operations and export creation/update. NULLFS is stackable: it owns a top export and delegates nearly every export operation to `export.sub_export` after temporarily switching `op_ctx->fsal_export` to the lower export.

## Important APIs, Types, and Functions

- `struct nullfs_fsal_export`: private wrapper around `struct fsal_export`.
- `release`: releases the lower export, drops the lower FSAL reference, detaches this export from the NULL FSAL, poisons ops, and frees the wrapper.
- Export capability pass-throughs: `get_dynamic_info`, `fs_supports`, `fs_maxfilesize`, `fs_maxread`, `fs_maxwrite`, `fs_maxlink`, `fs_maxnamelen`, `fs_maxpathlen`, `fs_acl_support`, `fs_supported_attrs`, `fs_umask`, `fs_expiretimeparent`, and `fs_readdir_mode`.
- Quota and state hooks: `get_quota`, `set_quota`, `nullfs_alloc_state`, and `nullfs_is_superuser`.
- Handle serialization hooks: `wire_to_host` and `nullfs_host_to_key`.
- Lifecycle hook: `nullfs_prepare_unexport`.
- `nullfs_export_ops_init`: installs all supported export operations.
- Configuration schema: `sub_fsal_params`, `export_params`, and `export_param` parse the nested lower `FSAL { name = ... }` block.
- `nullfs_create_export` and `nullfs_update_export`: create/update the lower export and stack it under NULLFS.

## Control Flow

Most export methods follow one pattern: recover `nullfs_fsal_export`, set `op_ctx->fsal_export` to `exp->export.sub_export`, call the lower export method, restore `op_ctx->fsal_export` to the NULL export, and return the result. `nullfs_create_export` parses the configured lower FSAL name, looks up that module, calls the lower module's `create_export`, releases the lookup reference, stacks the lower export with the newly allocated NULL export via `fsal_export_stack`, initializes default export ops, overwrites with NULLFS ops, and sets `op_ctx->fsal_export` to the new export. `nullfs_update_export` first calls the generic `update_export` to check stack changes, reparses lower FSAL config, and delegates update to the lower FSAL with `original->sub_export`.

## State and Persistence Behavior

The wrapper export stores its lower export in `export.sub_export`; the lower export's `super_export` points back through `fsal_export_stack`. The file mutates the thread-local request context while delegating. No data is persisted by NULLFS itself; export lifetime is managed through FSAL references, export lists, and explicit release.

## Dependencies and Integration Points

This file integrates with the config parser (`load_config_from_node`, `CONF_RELAX_BLOCK`, `subfsal_commit`), FSAL module registry (`lookup_fsal`, `fsal_put`), export manager, and common FSAL stacking helpers. It relies on lower FSAL export operations being complete and on `op_ctx` being initialized by request/config code.

## Risks and Edge Cases

- Every temporary `op_ctx->fsal_export` switch must be restored on all paths. The current simple wrappers restore after direct calls, but new error branches would need the same discipline.
- `release` assumes `sub_export` exists and has a valid release op.
- `nullfs_create_export` allocates `myself` before calling lower `create_export`; it frees on lower error, but lower create side effects remain lower-FSAL responsibility.
- Capability methods return lower-FSAL values, so NULLFS's static module info is less authoritative than export ops.
- `nullfs_alloc_state` uses `op_ctx->fsal_export = exp_hdl` for restore while most wrappers restore `&exp->export`; those are expected equivalent but worth preserving carefully.

## Test Signals

Tests should load a NULLFS export stacked over a real FSAL, verify capability queries reflect the lower FSAL, run reload/update with unchanged and changed lower config, exercise quota calls where supported, and unexport while checking for lower export release and no stale `op_ctx` after failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/export.c -->
