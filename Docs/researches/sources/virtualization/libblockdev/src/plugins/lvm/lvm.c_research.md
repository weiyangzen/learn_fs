# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm.c

## Role
Implements the public LVM plugin entry points for libblockdev. The file is a command-wrapper and parser layer around `lvm`, with additional direct `libdevmapper` use for logging and VDO stats support delegated to `vdo_stats.c`.

## Main Dependencies
- GLib for allocation, strings, mutexes, atomics, error domains, and pointer arrays.
- `blockdev/utils.h` for command execution, progress reporting, device helpers, and utility version checks.
- `libdevmapper` for DM logging setup.
- JSON-GLib for parsing `lvm --reportformat json_std`.
- Local `check_deps.h`, `dm_logging.h`, `lvm-private.h`, and `vdo_stats.h`.

## Dependency and Feature Gates
- `bd_lvm_init()` registers redirected device-mapper logging and sets verbosity based on `DEBUG`.
- `bd_lvm_close()` unregisters logging and clears cached dependency, feature, and module-dependency availability bits.
- `bd_lvm_is_tech_avail()` gates:
  - most operations on `lvm` at `LVM_MIN_VERSION`;
  - VDO on LVM VDO segtype, `dm-vdo` module, and `lvm`;
  - writecache on LVM writecache segtype and `lvm`;
  - devices-file operations on `lvmdevices`;
  - config queries on `lvmconfig >= 2.03.17`;
  - calculation-only techs as query-only and always locally available.

## Command Execution Model
- Internal wrappers prepend `lvm` to argument vectors and optionally append global `--config=<...>` and `--devices=<...>` settings.
- `global_config_lock` protects global LVM config/devices state during command construction and execution.
- Wrappers cover:
  - report-only execution with error propagation;
  - captured-output execution;
  - progress-reporting execution with a progress extractor.
- `call_lvm_and_parse_json_report()` centralizes JSON report parsing and returns a `JsonArray` owned by a caller-retained `JsonParser`.

## JSON Data Mapping
- `_lvm_json_get_string()` normalizes LVM empty string values to `NULL`.
- `get_pv_data_from_json()`, `get_vg_data_from_json()`, `get_lv_data_from_json()`, and `get_vdo_data_from_json()` map JSON report objects into the public structs declared in `lvm.h`.
- LV parsing normalizes internal LVM details:
  - maps `segtype=error` back to `linear` for missing-PV repair cases;
  - strips square brackets from internal pool/data/metadata LV names;
  - joins `lv_role` array values with commas;
  - supports tree output by parsing physical segment devices, sub-LVs, metadata devices, and segment PE sizes.
- `merge_lv_data()` merges repeated `lvs` rows from multi-segment LVs into one `BDLVMLVdata`.

## PV, VG, and LV Operations
- PV operations include create, resize, remove, move, scan, tags, single-PV info, and all-PV listing.
- VG operations include create, remove, rename, activate/deactivate, extend/reduce, tags, lock start/stop, single-VG info, and all-VG listing.
- LV operations include origin query, create, remove, rename, resize, repair, activate/deactivate, snapshot create/merge, tags, single/all LV info, and tree variants.
- Sizes passed to LVM are generally formatted as KiB strings (`%"G_GUINT64_FORMAT"K`) after dividing byte inputs by 1024.
- `bd_lvm_lvresize()` adds `--fs ignore` for LVM versions at or above `LVM_VERSION_FSRESIZE` to avoid filesystem checks.

## Thin, Cache, Writecache, and VDO
- Thin support creates thin pools, thin LVs, thin snapshots, queries a thin pool name, and converts data/metadata LVs into a thin pool.
- Cache support creates cache pool data and metadata LVs, converts them with `lvconvert --type cache-pool`, attaches/detaches cache pools, creates complete cached LVs, and extracts cache pool names from bracketed LVM output.
- Writecache support creates a fast cache LV plus data LV and attaches it via `lvconvert --type writecache`; attach explicitly deactivates both LVs first.
- VDO support creates VDO pools/LVs, toggles compression and deduplication, reports VDO info, resizes logical VDO LVs, only permits extension of physical VDO pool LVs, converts an existing LV into a VDO pool, and queries VDO pool names.
- VDO index memory and write policy are injected through temporary global LVM config because LVM exposes those settings through config rather than ordinary command arguments.

## Error and Semantics Notes
- Most operation failures are surfaced from libblockdev utility command helpers via `GError`.
- JSON parse failures use `BD_LVM_ERROR_PARSE`.
- VDO pool physical shrink is rejected before calling LVM with `BD_LVM_ERROR_NOT_SUPPORTED`.
- Cache-pool name extraction has explicit validation and reports `BD_LVM_ERROR_CACHE_INVAL` when LVM output is not bracketed as expected.

## Filesystem/Storage Relevance
This file is a high-level storage orchestration layer for block-device composition. It creates and mutates logical block devices that filesystems are later placed on, including thin provisioning, snapshots, cache tiers, writecache, VDO dedupe/compression, shared VG lockspaces, and device filtering.
