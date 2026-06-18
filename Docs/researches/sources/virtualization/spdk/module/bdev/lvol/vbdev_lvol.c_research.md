# File Research: sources/virtualization/spdk/module/bdev/lvol/vbdev_lvol.c

## Purpose
Implements the SPDK logical-volume bdev module. It maps blobstore lvol stores and lvol blobs to bdevs, handles lvstore load/create/unload/destroy, lvol create/snapshot/clone/resize/delete/rename/read-only operations, I/O forwarding, external snapshot support, shallow copy, hotplug, and asynchronous module shutdown.

## Main Entry Points
- `vbdev_lvs_create_ext()` and `vbdev_lvs_create()` create lvstores on base bdevs.
- `vbdev_lvs_unload()` and `vbdev_lvs_destruct()` unload or destroy lvstores.
- `vbdev_lvol_create()`, `vbdev_lvol_create_snapshot()`, `vbdev_lvol_create_clone()`, and `vbdev_lvol_create_bdev_clone()` create lvol bdevs from blobs, snapshots, or external-snapshot bdevs.
- `vbdev_lvol_destroy()`, `vbdev_lvol_rename()`, `vbdev_lvol_resize()`, and `vbdev_lvol_set_read_only()` mutate existing lvols.
- `vbdev_lvs_examine_disk()` loads lvstores discovered on base bdevs.
- `vbdev_lvs_examine_config()` handles external snapshot hotplug.
- `vbdev_lvol_shallow_copy()` and `vbdev_lvol_set_external_parent()` implement external-copy/parent operations.

## Internal Mechanics
`g_spdk_lvol_pairs` tracks loaded `lvol_store_bdev` pairs. Lookup helpers refuse lvstores with `removal_in_progress`, preventing new operations while unload/destroy is active. Creating an lvstore builds a blobstore bdev over the base bdev, initializes `spdk_lvs_opts`, sets external snapshot creation callback, claims the base bdev for the lvol module, and inserts the pair.

Each lvol bdev is a `struct lvol_bdev` whose public bdev name is `lvol->unique_id` and whose alias is `<lvs_name>/<lvol_name>`. Geometry is derived from blob cluster count, blobstore cluster size, and I/O unit size. The module forwards reads, writes, unmaps, and write-zeroes through blob I/O APIs and supports seek-data/seek-hole from blob allocation state. Writes, unmaps, and write-zeroes are hidden for read-only blobs.

Destroy/unload paths are asynchronous. Lvstore destroy recursively deletes deletable lvols, checks for circular clone dependencies, unregisters lvol bdevs, closes blobs, and finally unloads or destroys the blobstore. During global fini, `g_shutdown_started` allows the last lvol close to unload its lvstore and remove the registry entry.

External snapshot support validates esnap IDs as lower-case UUID strings, opens and claims the referenced bdev as a blobstore device when present, and otherwise returns a degraded dummy `spdk_bs_dev` that reports degraded state and no usable I/O. Missing esnap devices are registered for later hotplug; when the external bdev appears, clone trees are walked and bdevs are created for no-longer-degraded lvols.

Memory domain reporting includes base bdev domains and, for external snapshot clones, domains from the esnap bdev when it is available. Shallow copy creates and claims a destination bs_dev, starts `spdk_lvol_shallow_copy()`, then destroys the external device wrapper on completion.

## Dependencies
Uses SPDK bdev module APIs, blob/blobstore/lvol APIs, blob_bdev, UUID/string/log helpers, and internal lvolstore declarations.

## Risks and Notes
Alias rename happens before `spdk_lvol_rename()` completes; if the lvol rename later fails, alias state may already have changed. Degraded lvols do not register bdevs until their external snapshot is available, so RPC deletion has fallback lookup paths by UUID and `lvs/lvol` name. Clone deletion prevents removing an lvol with more than one clone relation. The degraded dummy bs_dev contains assert-failing I/O callbacks by design and must not be used for real I/O.
