# sources/object-store/openstack-swift/swift/container/sync_store.py

## Purpose

`swift/container/sync_store.py` implements the local filesystem index used by the container-sync daemon. Instead of scanning every container DB on every pass, sync-enabled DBs are represented by symlinks under each device's `sync_containers` tree. The container server and replicator update this store when sync metadata changes; the container-sync daemon iterates it.

## Important APIs, Types, and Functions

`SYNC_DATADIR = 'sync_containers'` is the per-device directory name parallel to the normal container `DATADIR`.

`ContainerSyncStore` exposes initialization, forward and reverse path conversion between real container DB paths and sync-store paths, `add_synced_container`, `remove_synced_container`, `update_sync_store`, and `synced_containers_generator`.

## Control Flow

Callers normally use `update_sync_store` after metadata or lifecycle changes. If neither sync metadata key has ever appeared, it returns without touching the filesystem. If the broker is deleted, it removes any sync symlink. If both sync target and key are non-empty, it creates a symlink. Otherwise it removes the symlink.

`add_synced_container` is idempotent: it returns when the symlink exists, creates parent directories when needed, and tolerates an `EEXIST` symlink race. `remove_synced_container` unlinks and removes empty parent directories, ignoring missing paths.

The daemon-side generator scans `sync_containers` DB entries and yields the corresponding real container DB path because `ContainerBroker` expects adjacent pending files and related artifacts in the real container directory.

## State and Persistence Behavior

The store persists no database records. Its durable state is the presence or absence of symlinks under `<devices>/<device>/sync_containers/.../<hash>.db` pointing at `<devices>/<device>/containers/.../<hash>.db`.

Directory cleanup uses `os.removedirs`, so only empty parent directories are removed. Metadata values remain authoritative; the filesystem index is a derived local cache.

## Dependencies and Integration Points

Dependencies are intentionally small: `audit_location_generator`, `mkdirs`, `DATADIR`, `os`, and `errno`.

Integration points are `server.py` metadata/delete handling, `replicator.py` post-replication and DB deletion handling, and `sync.py` discovery plus stale-link cleanup.

## Risks and Edge Cases

The path conversion helpers assume the normal Swift container DB layout and locate `DATADIR`/`SYNC_DATADIR` using `rfind`. Unexpected device paths containing those directory names elsewhere could confuse conversion.

If metadata keys exist with empty values, the symlink is removed. If metadata keys never existed, the method does nothing; callers should not rely on it to clean arbitrary stale symlinks for never-synced containers.

Symlink creation races are tolerated only when the existing path is a symlink. A regular file at the sync path is treated as an error.

Mount checking happens during generator scanning, not during add/remove operations.

## Test Signals

Useful tests should cover path conversion, idempotent add/remove behavior, add failure on non-symlink collision, `update_sync_store` decisions for never-synced, enabled, disabled, and deleted containers, and generator output of real DB paths with mount-check behavior.
