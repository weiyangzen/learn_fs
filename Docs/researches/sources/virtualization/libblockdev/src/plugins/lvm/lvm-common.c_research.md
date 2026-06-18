# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-common.c

## Purpose

`lvm-common.c` implements shared LVM plugin functionality used by both backend variants. It contains data copy/free helpers, LVM sizing calculations, global LVM configuration state, devices-file helpers, enum/string conversion helpers, VDO statistics glue, VG config backup/restore wrappers, and cache status parsing through device-mapper.

## Data Lifetime Helpers

The file provides deep copy and free functions for public LVM data structures:

- `BDLVMPVdata`
- `BDLVMVGdata`
- `BDLVMSEGdata`
- `BDLVMLVdata`
- `BDLVMVDOPooldata`
- `BDLVMCacheStats`

LV copy/free logic handles nested string vectors and segment arrays through private `copy_segs()` and `free_segs()` helpers.

## Size and Validity Calculations

The file defines reusable calculation APIs for LVM callers:

- supported PE sizes from 1 KiB to 16 GiB
- max LV size, differing for 64-bit and 32-bit builds
- rounding arbitrary byte sizes to PE boundaries
- LV physical size calculation
- thin-pool padding and metadata size estimates
- thin-pool metadata size validation
- thin-pool chunk size validation, including stricter power-of-two behavior when discard support is required
- default cache metadata size, at least 8 MiB or 0.1% of cache size

The shared constants include `SECTOR_SIZE`, `DEFAULT_PE_SIZE`, thin-pool metadata bounds, thin-pool chunk bounds, and cache metadata minimums.

## Global Config and Device Filtering

`global_config_lock`, `global_config_str`, and `global_devices_str` hold process-local libblockdev LVM configuration. These settings do not modify system `lvm.conf`; they are injected into later LVM calls as `--config` and `--devices`.

The APIs are:

- `bd_lvm_set_global_config()`
- `bd_lvm_get_global_config()`
- `bd_lvm_set_devices_filter()`
- `bd_lvm_get_devices_filter()`

The devices filter checks `BD_LVM_TECH_DEVICES` availability before storing a comma-separated device list.

## Enum and String Conversion

The file maps LVM cache and VDO enums to strings and back where needed:

- cache mode: `writethrough`, `writeback`, `unknown`
- VDO operating mode: `recovering`, `read-only`, `normal`, `unknown`
- VDO compression state: `online`, `offline`, `unknown`
- VDO index state: `error`, `closed`, `opening`, `closing`, `offline`, `online`, `unknown`
- VDO write policy: `auto`, `sync`, `async`, `unknown`

Invalid values populate `BD_LVM_ERROR`.

## VDO Statistics

`bd_lvm_vdo_get_stats_full()` builds the kernel dm-vdo map name as `<vg>-<pool>-vpool` and delegates to `vdo_get_stats_full()`.

`bd_lvm_vdo_get_stats()` converts selected hashtable entries into a fixed `BDLVMVDOStats` structure. Missing numeric values are represented with `-1`, and `writeAmplificationRatio` falls back to `-1` if unavailable.

## LVM Devices File Helpers

`_lvm_devices_enabled()` checks whether the LVM devices file is enabled by querying `lvmconfig`. It first checks full config, including libblockdev's global config, then falls back to default config.

`bd_lvm_devices_add()` and `bd_lvm_devices_delete()` wrap `lvmdevices --adddev` and `lvmdevices --deldev`, optionally passing `--devicesfile=<file>`. They fail with `BD_LVM_ERROR_DEVICES_DISABLED` if the devices file feature is not active.

## Config and Backup/Restore Helpers

`bd_lvm_config_get()` wraps `lvmconfig`, allowing section/setting selection, type selection, values-only output, optional global-config injection, and arbitrary extra arguments.

`_vgcfgbackup_restore()` is the shared implementation for:

- `bd_lvm_vgcfgbackup()`
- `bd_lvm_vgcfgrestore()`

Both call `lvm vgcfgbackup` or `lvm vgcfgrestore`, optionally with `-f <file>`, and include global config when set.

## Cache Stats

`bd_lvm_cache_stats()` queries a cached LV with libdevmapper:

1. Calls `bd_lvm_lvinfo()` to determine whether the cached object is a thin pool data LV or a normal cached LV.
2. Builds the device-mapper name with `dm_build_dm_name()`.
3. Runs a `DM_DEVICE_STATUS` task.
4. Parses cache target parameters with `dm_get_status_cache()`.
5. Converts sector-based block counts into bytes.
6. Detects writethrough/writeback mode from feature flags.

Failures are reported as `BD_LVM_ERROR_DM_ERROR`, `BD_LVM_ERROR_CACHE_NOCACHE`, or `BD_LVM_ERROR_CACHE_INVAL`.

## Research Notes

This file is backend-independent glue. It is storage-stack relevant because it encodes LVM sizing policy, device-filter behavior, cache and VDO metadata interpretation, and device-mapper status conversion used by higher-level block and filesystem provisioning workflows.
