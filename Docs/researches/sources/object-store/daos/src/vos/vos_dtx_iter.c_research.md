# sources/object-store/daos/src/vos/vos_dtx_iter.c

## Purpose
`vos_dtx_iter.c` implements the `VOS_ITER_DTX` iterator over active DTX entries. It exposes prepared, unresolved DTXs to upper-layer resync and cleanup logic while filtering entries that are committed, aborted, currently preparing, or attached to a live DTX handle.

## Important APIs, Types, And Functions
- `struct vos_dtx_iter` embeds `struct vos_iterator`, stores a dbtree iterator handle, referenced container, current active entry for linear mode, and a mode flag.
- `dtx_iter_prep()` validates iterator type, resolves the container handle, takes a container reference, and prepares a dbtree iterator over `vc_dtx_active_hdl`.
- `dtx_iter_probe()` starts either linear list iteration from `vc_dtx_act_list` for a zero anchor or dbtree iteration for a nonzero anchor.
- `dtx_iter_next()` advances through the selected backend and skips non-returnable DTX entries.
- `dtx_iter_fetch()` fills `vos_iter_entry_t` with DTX id, oid, epoch, version, flags, start time, dkey hash, and membership data.
- `dtx_iter_process()` rejects delete through iteration.

## Control Flow
The iterator has two paths. With a zero anchor, it walks `vc_dtx_act_list` directly and records the current `vos_dtx_act_ent`; this is a linear in-memory scan. With a nonzero anchor, it probes the active DTX btree with `BTR_PROBE_GE` and fetches by anchor. Both `probe` and `next` skip entries that are already commit/abort states, still `dae_preparing`, or currently attached to a live `dae_dth`. Fetch asserts the returned entry is prepared/unattached/uncommitted/unaborted, marks `dae_need_validation` to protect against later races with RPC handling, and returns inline or out-of-line membership data depending on `DAE_MBS_DSIZE()`.

## State And Persistence Behavior
This file does not modify durable DTX blobs. Its visible mutation is `dae_need_validation = 1`, which forces later DTX handlers to revalidate before becoming committable or committed. It holds a container reference for iterator lifetime and closes the dbtree iterator during finish.

## Dependencies And Integration Points
The iterator depends on VOS iterator framework, active DTX btree, active DTX list, container reference management, DTX layout macros, and umem pointer conversion for out-of-line membership data. It is intended for DTX resync and cleanup consumers that enumerate prepared DTXs.

## Risks And Edge Cases
- Linear list and btree iteration must apply identical skip rules.
- Returning membership pointers points directly into active DTX memory or umem-mapped membership storage, so iterator lifetime and container lifetime matter.
- The iterator intentionally forbids deletion; cleanup must use DTX-specific APIs to preserve commit/abort semantics.
- Marking `dae_need_validation` is a race mitigation but also changes later DTX-handle behavior.

## Test Signals
Test zero-anchor list iteration, anchored btree iteration, skip behavior for commit/abort/preparing/attached entries, fetch of inline and out-of-line memberships, validation flag setting, finish reference release, and delete rejection with `-DER_NO_PERM`.
