
# sources/user-network-fs/nfs-ganesha/src/SAL/state_layout.c

## Purpose

`state_layout.c` manages pNFS layout state segments in SAL. It adds and removes layout segments, finds existing layout state for a file/client/layout type, and revokes all layouts owned by a client during cleanup such as lease expiry.

## Important APIs, types, and functions

- `state_add_segment()` adds an FSAL-provided `pnfs_segment` and FSAL private data to a `STATE_TYPE_LAYOUT` state.
- `state_delete_segment()` removes and frees one `state_layout_segment_t`.
- `state_lookup_layout_state()` searches a file's state list for a layout state matching owner and layout type and returns it with an incremented ref.
- `revoke_owner_layouts()` iterates a client owner state list and returns every layout with `nfs4_return_one_state()` using `circumstance_revoke`.

## Control flow

Segment add validates that the target state is layout state, allocates a segment object, copies the segment, links it to `state_data.layout.state_segments`, and marks the whole layout state `return_on_close` if any segment requests that behavior. Delete unlinks and frees a segment.

Lookup walks `obj->state_hdl->file.list_of_states` under the caller-held state lock and compares state type, owner, and layout type. On match it increments the state reference and returns success.

Owner revoke loops over the client's state list under `so_mutex`, moves each inspected entry to the tail to avoid spinning on skipped/error entries, skips non-layout states, obtains object/export refs, sets op context to the export, drops `so_mutex`, locks the object state, calls `nfs4_return_one_state()` for the entire file byte range and any I/O mode, then releases refs and restarts because the owner list lock was dropped.

## State and persistence behavior

Layout state is in memory only. Segments are linked under a layout `state_t`; FSAL-specific segment data is stored as an opaque pointer but not freed here. Revocation returns layouts to the client/FSAL path and deletes state through `nfs4_return_one_state()` if successful. No persistent recovery records are written by this file.

## Dependencies and integration points

The file depends on SAL state structures, glist, object state locks, owner refs, export context helpers, pNFS segment definitions, and NFSv4 layoutreturn logic. It is called by NFSv4.1 LAYOUTGET/LAYOUTRETURN and lease/client cleanup paths.

## Risks and edge cases

- `state_delete_segment()` frees only the segment wrapper, not `sls_fsal_data`; ownership must be handled elsewhere.
- `revoke_owner_layouts()` restarts after dropping `so_mutex`; the tail-moving and `first` sentinel reduce but do not eliminate complexity around concurrent list changes.
- Revoke aborts with `LogFatal()` after `STATE_ERR_MAX` failed layout returns, making persistent cleanup failure process-fatal.
- Correct lock ordering between owner mutex, object state lock, and export context is crucial.

## Test signals

Tests should cover segment add/delete, non-layout add rejection, return-on-close propagation, lookup by owner/type, refcounting on lookup, revoke of multiple layouts with intervening non-layout states, stale state/object handling, `nfs4_return_one_state()` deletion success/failure, and concurrency with owner state-list mutation.
