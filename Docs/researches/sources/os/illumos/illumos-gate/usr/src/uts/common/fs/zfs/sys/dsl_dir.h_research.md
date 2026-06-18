# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dsl_dir.h

Read status: complete, 212 lines.

Purpose: DSL directory physical/in-core definitions and namespace/space-accounting APIs.

Key structures and APIs:
- Extensible ZAP fields include filesystem count, snapshot count, last remap TXG, and crypto key object.
- `dd_used_t` partitions used space into head, snapshots, children, child reservation, and refreservation.
- `dsl_dir_phys_t` stores head dataset object, parent/origin/children ZAP links, used/compressed/uncompressed bytes, quota/reservation, properties/delegation objects, flags, used breakdown, clones object, and padding.
- `dsl_dir_t` stores dbuf user, object, crypto object, pool, dbuf, dirty link, parent, lock, property callbacks, snapshot cmtime, origin txg, temporary reservations, expected dirty space, and name.
- APIs cover hold/release/name/create, space/stat getters, origin/count/remap TXG getters, stats export, available-space calculation, dirty/sync, temp reservations, will/did-use accounting, space transfer, quota/reservation setters, fs/snapshot limit activation/check/count adjust, last remap TXG update, rename, transfer feasibility, clone detection, refreservation updates, snapshot cmtime, zapification, and debug logging.

Important implementation constraints:
- `dd_parent` is protected by pool config lock.
- `dd_lock` protects property callbacks, snap cmtime, origin txg, temp reservations, expected dirty space, and name.
- Temporary reservations are per TXG.

Dependencies: DMU, DSL pool, DSL synctask, refcount, ZFS context, DSL crypto.

Research notes:
- DSL dirs are the namespace and hierarchical accounting layer above datasets.
- Reserved internal names include `$MOS`, `$ORIGIN`, `$FREE`, and `$LEAK`.
