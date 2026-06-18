# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dataset.h

Read status: complete, 488 lines.

Purpose: DSL dataset physical/in-core definitions and dataset lifecycle/accounting APIs.

Key structures and APIs:
- Dataset flags track inconsistency, no-promote, unique-byte accuracy, deferred destroy, case-insensitive dataset, and create-no-dirty.
- `DS_FIELD_*` strings define extensible ZAP fields for bookmarks, large dnodes, resumable receive state, remap deadlist, and encrypted snapshot IV-set GUID.
- `dsl_dataset_phys_t` stores directory linkage, previous/next snapshot linkage, snapshot names object, child count, creation time/TXG, deadlist object, referenced/compressed/uncompressed/unique bytes, fsid/guid, flags, root block pointer, clone/properties/userrefs objects, and padding.
- `dsl_dataset_t` stores dbuf user, root block pointer lock, immutable dir/object/fsid/snapshot/key mapping state, previous snapshot, bookmarks object, deadlists, remap deadlist, dirty/synced links, object/open/userref/owner/quota/reservation/sendstream/resume/prop/feature state, and snapname.
- Argument structs support promote, rollback, and snapshot operations.
- APIs cover hold/own/release/disown, key mapping, create, snapshot, promote, clone swap, rename snapshots, temporary snapshots, block pointer/spa access, sync, block born/kill/remapped, dirtying, stats getters, quota/refreservation setters, long holds, clone-swap/snapshot internals, snap lookup/remove, zapification, resumable receive detection, rollback, remap deadlist management, per-dataset feature activation/deactivation/query, and debug logging.

Important implementation constraints:
- `ds_bp_rwlock` protects `ds_phys->ds_bp`.
- Long holds prevent dataset destruction after config lock is dropped.
- `ds_remap_deadlist` tracks physical DVAs remapped away from indirect vdevs for obsolete-count accounting.
- Per-dataset features use `ds_feature[]` and `ds_feature_activation[]`.

Dependencies: DMU, SPA, TXG, ZIO, bplist, DSL synctask, deadlist, refcount, rrwlock, DSL crypto, feature definitions.

Research notes:
- This is the central DSL object for snapshots, clones, send/receive resume state, quota/refreservation accounting, deadlists, and per-dataset features.
