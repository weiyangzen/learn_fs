# File Research: sources/virtualization/spdk/lib/lvol/lvol.c

Implements SPDK logical volume stores and logical volumes on top of blobstore, including lvolstore create/load/unload/destroy/grow/rename, lvol create/open/close/destroy/resize/rename, snapshots, clones, external snapshots, degraded external-snapshot tracking, shallow copy, and parent management.

Key entry points:
- `spdk_lvs_opts_init()`, `spdk_lvs_init()`, `spdk_lvs_load()`, and `spdk_lvs_load_ext()` initialize or load lvolstores.
- `spdk_lvs_rename()`, `spdk_lvs_unload()`, `spdk_lvs_destroy()`, `spdk_lvs_grow()`, and `spdk_lvs_grow_live()` manage lvolstore lifecycle and capacity changes.
- `spdk_lvol_create()`, `spdk_lvol_create_esnap_clone()`, `spdk_lvol_open()`, `spdk_lvol_close()`, `spdk_lvol_destroy()`, `spdk_lvol_resize()`, `spdk_lvol_rename()`, and `spdk_lvol_set_read_only()` manage individual lvol lifecycle and metadata.
- `spdk_lvol_create_snapshot()` and `spdk_lvol_create_clone()` expose blobstore snapshot/clone operations as lvol operations.
- `spdk_lvol_inflate()` and `spdk_lvol_decouple_parent()` materialize shared data or sever clone parentage.
- `spdk_lvs_esnap_missing_add()`, `spdk_lvs_esnap_missing_remove()`, and `spdk_lvs_notify_hotplug()` track and retry missing external snapshots.
- `spdk_lvol_iter_immediate_clones()`, `spdk_lvol_get_by_uuid()`, `spdk_lvol_get_by_names()`, and `spdk_lvol_is_degraded()` provide lookup/introspection helpers.
- `spdk_lvol_shallow_copy()`, `spdk_lvol_set_parent()`, and `spdk_lvol_set_external_parent()` handle data export and parent reassignment.

Core mechanics:
- A process-global `g_lvol_stores` list tracks loaded lvolstores by name under `g_lvol_stores_mutex`; each store also records the SPDK thread that created/loaded it.
- Each lvolstore has a blobstore plus a super blob whose xattrs store the lvolstore UUID and name. Loading opens the super blob, validates those xattrs, inserts the store globally, then iterates blobs to rebuild the lvol list.
- Individual lvol blobs store `name` and `uuid` xattrs. If an older/corrupt blob lacks a valid UUID, `unique_id` falls back to `<lvs_uuid>_<blob_id>`.
- New lvols are first placed on `pending_lvols` to reserve names while asynchronous blob creation is in progress, then moved to `lvols` once the blob opens successfully.
- Blobstore options are wrapped by lvolstore options, including cluster size, clear method, metadata page sizing, and optional external-snapshot bs_dev creation callbacks.
- The options-copy helper uses `opts_size` and a static size assertion to preserve ABI compatibility as fields are added.
- Snapshot and clone creation allocate a new lvol object, attach xattr callbacks for name/UUID, and delegate to blobstore snapshot/clone APIs.
- Destroy checks open references and clone relationships. If a degraded external-snapshot clone is deleted, degraded-set membership may transfer to its remaining clone.
- Open/close reference counting avoids reopening an already open blob and closes the blob only when the last reference is dropped.

External snapshot and degraded-mode mechanics:
- `lvs_esnap_bs_dev_create()` bridges blobstore external-snapshot callbacks to the lvolstore's registered `esnap_bs_dev_create` callback.
- During initial lvolstore load, `load_esnaps` is false so external snapshot devices are not opened while enumerating blobs; it is set true once loading completes.
- Missing external snapshots are stored in a red-black tree keyed by external snapshot ID bytes. Each tree node owns a tailq of lvols degraded by that same missing snapshot.
- `spdk_lvs_notify_hotplug()` searches lvolstores on the current thread for a matching degraded set and tries to attach the newly available external snapshot device to each lvol blob.
- Hotplug retry temporarily removes an lvol from the degraded tailq before invoking the callback, preventing tailq corruption if the callback re-adds the lvol on failure.

Important invariants:
- Lvolstore names must be unique globally, including pending `new_name` values during rename.
- Lvol names must be non-empty, null-terminated within `SPDK_LVOL_NAME_MAX`, and unique across both active and pending lvols in the store.
- Lvolstore unload and destroy reject stores with pending lvol actions or open lvol references.
- Most external-snapshot degraded-set operations assert they run on the lvolstore's owning SPDK thread.
- Removed degraded-set nodes are freed only after their lvol tailq becomes empty.
- `spdk_lvol_set_external_parent()` rejects an external snapshot ID that is identical to the lvol's own UUID string.

Filesystem/block relevance:
- This is SPDK's logical volume manager. It provides thin provisioning, snapshots, clones, parent/child relationships, and degraded external snapshot recovery for blobstore-backed virtual block devices.

Notable risks:
- The file is callback-heavy; failures in late async stages often rely on carefully paired cleanup callbacks to avoid leaked lvol objects, blobstore handles, or global list entries.
- Some global lookups return lvol pointers after releasing `g_lvol_stores_mutex`, so callers rely on higher-level SPDK threading/lifetime rules for safety.
- `spdk_lvs_destroy()` frees lvol structs without removing each from the list first because the whole store is being destroyed; this is correct only if no later code walks that list before `lvs_free()`.
- Degraded external-snapshot handling is explicitly thread-affine. Notifications from the wrong thread are discarded with a notice, which can leave lvols degraded until a correct-thread notification occurs.
