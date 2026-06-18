# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devid_cache.c

## Purpose

`devid_cache.c` implements the kernel-side device-id cache for illumos. It maintains the in-memory mapping between persistent physical device paths and DDI device identifiers, serializes that mapping to `/etc/devices/devid_cache` through the `nvf` cache-file framework, and provides lookup paths used by layered device consumers that need stable device identity even after hardware has moved.

The file is also responsible for controlled "discovery": expensive device-tree probing used when a requested devid is not currently reachable through cached paths.

## Main Interfaces

- `devid_cache_init()` registers the nvf backing file, initializes the cache list, and sets up discovery synchronization.
- `devid_cache_read()` loads persisted cache contents unless disabled by `devid_cache_read_disable`.
- `e_ddi_devid_discovery()` serializes full-tree or driver-targeted discovery attempts using `devid_discovery_mutex` and `devid_discovery_cv`.
- `e_devid_cache_register()`, `e_devid_cache_pathinfo()`, and `e_devid_cache_unregister()` add, refresh, or detach devinfo references for path/devid mappings.
- `devid_cache_cleanup()` removes cache entries that never registered in the current boot.
- `e_devid_cache_to_devt_list()` returns sorted, duplicate-collapsed `dev_t` lists for a devid and minor name.
- `e_devid_cache_free_devt_list()` frees lists returned by `e_devid_cache_to_devt_list()`.
- `e_devid_cache_path_to_devid()` performs reverse lookup from a full path, or from parent path plus unit address, to a duplicated devid.

## Cache Format And State

The cache file stores an nvlist keyed by device path. Each child nvlist has a byte-array `DP_DEVID_ID` value containing the packed `ddi_devid_t`. `devid_cache_unpack_nvlist()` validates each decoded devid before inserting an `nvp_devid_t` into the cache list. `devid_cache_pack_list()` walks the list and rebuilds the nvlist for persistence.

Each in-memory entry tracks:

- `nvp_devpath`: persistent path string.
- `nvp_devid`: kernel copy of the device id.
- `nvp_flags`: whether the entry has a current devinfo pointer and whether it registered this boot.
- `nvp_dip`: current devinfo pointer when available.

The list is protected by `nvf_lock(dcfd_handle)`, with writers used for mutation and readers for lookup.

## Registration Behavior

`e_devid_cache_register_cmn()` accepts either a `dip` or an explicit path. It duplicates the path and devid, then searches for an existing path match:

- If the existing path has no devid or an invalid devid, it replaces the devid.
- If the path already maps to the same devid, it marks the entry registered and associates the `dip`.
- If the path maps to a different valid devid, it logs both encoded devids, removes the stale entry, and inserts the new mapping.
- New or replaced mappings mark the nvf cache dirty and wake the nvf daemon unless writes are disabled.

This enforces the invariant that one path maps to one devid, while allowing one devid to map to multiple paths.

## Discovery Model

Discovery is intentionally rate-limited and serialized. Before root I/O is initialized, `e_devid_do_discovery()` consumes `devid_discovery_boot`. After boot, it honors `devid_discovery_postboot_always`, then `devid_discovery_postboot`, then the `devid_discovery_secs` minimum interval.

Pre-root discovery holds likely installed drivers using the devid's driver hint, drivers marked `DN_DEVID_REGISTRANT`, and a legacy list containing `sd` and `ssd`. Post-root discovery invokes `ndi_devi_config()` on the root node with persistent config flags and optionally `NDI_DRV_CONF_REPROBE`.

## Lookup Flow

`e_devid_cache_to_devt_list()` first calls `e_devid_cache_devi_path_lists()` under the cache read lock. That helper returns held devinfo nodes for attached devices and path strings for stale or unattached entries. Path strings are duplicated before releasing the cache lock.

The function then:

1. Enumerates matching minor nodes from held devinfo nodes.
2. Resolves cached paths with `e_ddi_hold_devi_by_path()`.
3. Verifies newly attached devices still register the requested devid.
4. Builds a `dev_t` array, retrying with a larger allocation when necessary.
5. Bubble-sorts the result and collapses duplicates before returning it.

This design avoids returning transient implementation duplicates to consumers such as SVM namespace code.

## Reverse Path Lookup

`e_devid_cache_path_to_devid()` supports two modes:

- Full path exact match when `ua == NULL`.
- Parent-path plus unit-address match when `ua != NULL`, treating the node name between the final slash and `@` as unknown.

On match it duplicates the cached devid for the caller and optionally returns the node name in `nodenamebuf`.

## Dependencies

This file depends on DDI/NDI device tree APIs, MDI pathinfo support, `nvf` cache-file management, nvlist packing, devinfo hold/release helpers, and devid encode/compare/validate routines. It also depends on the wider device configuration system through `devnamesp`, `devcnt`, `ddi_hold_installed_driver()`, and `ndi_devi_config()`.

## Notable Invariants And Audit Notes

- `nvf_lock(dcfd_handle)` protects the cache list and must be held according to read/write intent.
- Registered `nvp_dip` pointers are only used after parent `ndi_devi_tryenter()` succeeds and the devinfo node is held.
- Discovery is single-flight; waiters block until the active discovery completes.
- Returned devinfo holds from cache scans are released after devt enumeration.
- `devid_cache_cleanup()` marks stale removals dirty but sets `is_dirty = 0` in that branch, so the final `nvf_wake_daemon()` path is not reached for cleanup removals. That is a focused audit point because it may affect persistence timing.
- `e_devid_cache_free_devt_list()` frees with `ndevts * sizeof (dev_t *)` while allocation uses `sizeof (dev_t)`. This is harmless only if those sizes match on the target ABI.
