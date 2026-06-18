# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_synctask.c

## Role
Implements the ZCP `zfs.check` and `zfs.sync` submodules. It wraps existing DSL check/sync operations for destroy, promote, rollback, snapshot, property inherit, user-property set, and encryption key change.

## Generic Sync Wrapper
- `zcp_sync_task()` runs a DSL check function against the current channel-program transaction.
- If `sync` is false, it returns only the check result for dry-run behavior.
- If `sync` is true but the channel program is not running in sync context, it raises a Lua error explaining that `zfs.sync` requires sync evaluation.
- If check succeeds, it calls the sync function; I/O errors become fatal Lua errors with dataset context.

## Exposed Operations
- `destroy`: destroys snapshots or filesystem heads; `defer` kwarg is accepted only for snapshots.
- `promote`: promotes a clone and can return conflict details through `err_details`.
- `rollback`: rolls back a filesystem and can return details through `err_details`.
- `snapshot`: creates a single snapshot, rejects pools older than `SPA_VERSION_FAST_SNAP`, and uses cleanup handlers for the snapshot nvlist.
- `inherit`: validates user or inheritable non-readonly properties and calls DSL property inherit sync.
- `set_prop`: delegates check/sync to `zcp_set.c`, limited to user properties.
- `change_key`: parses raw/hex key format, creates crypto params via `zcp_change_key.c`, and delegates keystore check/sync.

## Space Accounting
- Each operation declares a `space_check` class and rough `blocks_modified`.
- `zcp_synctask_wrapper()` estimates MOS space as `blocks_modified << DST_AVG_BLKSHIFT` times 3 for triple ditto blocks.
- The wrapper tracks cumulative `zri_space_used` to prevent a channel program from exceeding unreserved pool space across multiple operations.

## Lua Registration
- `zcp_load_synctask_lib(state, sync)` creates a table of operation closures.
- The same operation table is loaded twice by `zcp.c`: once as `zfs.check` with `sync=false`, and once as `zfs.sync` with `sync=true`.
- `zcp_synctask_wrapper()` parses args, allocates `err_details`, registers cleanup, runs the operation, returns errno as first Lua result, and optionally returns details as a second result.

## Important Details
- Cleanup handlers protect nvlists and crypto params from Lua longjmp leaks.
- The wrapper returns operation errors to Lua as numeric errno values for script handling, except fatal context/I/O errors.
- Snapshot creation supports only a single snapshot name rather than a batch list.
