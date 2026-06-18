# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-dbus.c

## Purpose

`lvm-dbus.c` implements the libblockdev LVM plugin backend using `lvmdbusd` over the system D-Bus. It exposes the public `bd_lvm_*` API by translating operations into lvmdbusd object lookups, property reads, method calls, and asynchronous job polling.

## D-Bus Model

The file defines object prefixes and interfaces for:

- manager: `/com/redhat/lvmdbus1/Manager`
- PVs, VGs, LVs, hidden LVs, thin pools, cache pools, and VDO pools
- job objects under `/com/redhat/lvmdbus1/Job/`
- standard D-Bus properties and introspection interfaces

A static `GDBusConnection *bus` is initialized against the system bus. `bd_lvm_init()` sets up this connection and initializes libdevmapper logging; `bd_lvm_close()` flushes/closes the connection, resets dependency caches, and disables devmapper log redirection.

## Dependency and Feature Checks

The backend caches availability checks for:

- utilities: `lvm`, `lvmdevices`, `lvmconfig`
- D-Bus service: `com.redhat.lvmdbus1`
- lvmdbusd version needed for writecache
- LVM segtypes: `vdo`, `writecache`
- kernel module: `dm-vdo`

`bd_lvm_is_tech_avail()` maps each `BDLVMTech` to required dependencies. Pure calculation techs are always available for query mode; VDO requires lvmdbusd, LVM VDO feature support, and `dm-vdo`.

## Core Call Flow

The main helper is `call_lvm_method()`:

1. Verifies lvmdbusd availability.
2. Optionally locks `global_config_lock`.
3. Merges extra parameters, `BDExtraArg` entries, global `--config`, and global `--devices` into lvmdbusd's extra-argument dictionary.
4. Appends a one-second lvmdbusd timeout and the extra dictionary to the method parameter tuple.
5. Logs task status and starts progress reporting.
6. Calls the requested D-Bus method synchronously.

`call_lvm_method_sync()` handles the result. It accepts immediate object results, immediate no-result success, or job object paths. For jobs, it polls `Complete`, reports `Percent`, reads `Result`, fetches `GetError` on failure, and removes the job object afterward.

Convenience wrappers dispatch by object id, LV, thin pool, and VDO pool.

## Object Lookup and Property Parsing

The backend uses lvmdbusd manager `LookUpByLvmId` to map LVM IDs such as `vg/lv` or `/dev/sda` to object paths. It uses D-Bus `Get` and `GetAll` for property access, and `Introspect` to enumerate objects under PV/VG/LV/pool prefixes.

Property decoders build libblockdev structures:

- `get_pv_data_from_props()` fills PV fields, tags, missing state, and related VG details.
- `get_vg_data_from_props()` fills VG size, free space, extent counts, PV count, tags, and exportable state.
- `get_lv_data_from_props()` fills LV identity, size, attr, percents, segtype, roles, VG name, origin, pool, move PV, and tags.
- `get_vdo_data_from_props()` maps lvmdbusd VDO mode/state/policy strings and boolean-like feature strings into `BDLVMVDOPooldata`.

Extra LV helpers discover pool data LVs, metadata LVs, segment placement, hidden image/metadata LVs, and related VG names by chasing object-path properties.

## PV Operations

The file implements:

- `bd_lvm_pvcreate()`
- `bd_lvm_pvresize()`
- `bd_lvm_pvremove()`
- `bd_lvm_pvmove()`
- `bd_lvm_pvscan()`
- PV tag add/delete
- `bd_lvm_pvinfo()`
- `bd_lvm_pvs()`

Notable behavior: `bd_lvm_pvremove()` uses `-ff` and `--yes`; if lvmdbusd reports the PV object does not exist, removal is treated as a successful no-op for a non-PV device.

## VG Operations

The file implements:

- `bd_lvm_vgcreate()`
- `bd_lvm_vgremove()`
- `bd_lvm_vgrename()`
- `bd_lvm_vgactivate()` / `bd_lvm_vgdeactivate()`
- `bd_lvm_vgextend()` / `bd_lvm_vgreduce()`
- VG tag add/delete
- lockspace start/stop via `--lockstart` and `--lockstop`
- `bd_lvm_vginfo()`
- `bd_lvm_vgs()`

VG creation converts PV names to object paths and injects `--physicalextentsize` using the resolved PE size. Reducing missing PVs passes a force extra parameter.

## LV Operations

The basic LV API includes:

- origin query
- create/remove/rename/resize/repair
- activate/deactivate
- classic snapshot create/merge
- tag add/delete
- LV info and LV tree info
- LV listing with optional VG filtering

LV creation supports optional type and PV placement. For striped LVs with an explicit PV list, the code passes `stripes=<pv_count>` instead of a generic type option. LV resize adds `--fs ignore` when the installed LVM version is at least `2.03.19`, avoiding filesystem-related resize checks.

LV listing merges objects from normal LV, thin-pool, cache-pool, VDO-pool, and hidden-LV namespaces. `bd_lvm_lvs_tree()` additionally populates segment and hidden data/metadata LV arrays.

## Thin Provisioning

Thin-related operations include:

- `bd_lvm_thpoolcreate()`
- `bd_lvm_thlvcreate()`
- `bd_lvm_thlvpoolname()`
- `bd_lvm_thsnapshotcreate()`
- `bd_lvm_thpool_convert()`

Thin pool creation uses lvmdbusd `LvCreateLinear` with thin-pool-specific extra options such as `poolmetadatasize`, `chunksize`, and `profile`. Converting an existing data and metadata LV into a thin pool calls `CreateThinPool`, then optionally renames the resulting pool.

## Cache and Writecache

Cache support includes:

- cache pool creation from data and metadata LVs
- attaching and detaching cache pools
- combined cached-LV creation
- cache pool name discovery
- converting existing LVs into a cache pool

`bd_lvm_cache_create_pool()` is a multi-step workflow: create the cache data LV, create the metadata LV, then call `CreateCachePool`. It reports progress at each stage.

Writecache support includes:

- `bd_lvm_writecache_attach()`
- `bd_lvm_writecache_detach()`
- `bd_lvm_writecache_create_cached_lv()`

Writecache attach explicitly deactivates both the data LV and cache LV before calling `WriteCacheLv`.

## VDO

VDO support includes:

- `bd_lvm_vdo_pool_create()`
- compression enable/disable
- deduplication enable/disable
- `bd_lvm_vdo_info()`
- virtual LV resize
- physical pool resize
- conversion of an existing LV into a VDO pool
- VDO LV pool-name query

VDO creation and conversion pass compression/deduplication as extra parameters. Index memory and write policy are injected by temporarily extending `global_config_str` under `global_config_lock`, because these settings are only available through LVM config. Physical VDO pool resize refuses reductions with `BD_LVM_ERROR_NOT_SUPPORTED`.

## Compatibility and Edge Cases

The code contains several explicit compatibility choices:

- Calculation techs are available without lvmdbusd.
- LV segtype arrays are simplified by using the first segment type; `"error"` is normalized to `"linear"`.
- PV tags must be modified through the owning VG interface, so unassigned PVs cannot be tagged.
- Cache pool names are parsed from bracketed hidden LV names.
- VDO default pool/LV names are synthesized when callers pass `NULL`.
- Several operations use extra options to avoid interactive prompts or filesystem handling.

## Research Notes

This file is a high-level block storage orchestration backend. It does not implement filesystems directly, but it provisions and modifies the LVM devices on which filesystems are created, resized, snapshotted, cached, thin-provisioned, or exposed to virtualization stacks.
