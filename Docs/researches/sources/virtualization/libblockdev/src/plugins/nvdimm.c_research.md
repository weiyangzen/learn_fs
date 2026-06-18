# File Research: sources/virtualization/libblockdev/src/plugins/nvdimm.c

## Role
Implements the deprecated NVDIMM plugin. It uses libndctl for most namespace discovery and state operations, and uses the `ndctl` CLI only for namespace reconfiguration.

## Main Dependencies
- GLib and blockdev utilities.
- `ndctl/libndctl.h` for bus, region, namespace, BTT, PFN, and DAX operations.
- `uuid.h` for namespace/BTT/PFN/DAX UUID extraction.
- Runtime `ndctl` tool for reconfigure mode.

## Lifecycle and Availability
- `bd_nvdimm_init()` is a no-op; `bd_nvdimm_close()` clears cached dependency state.
- `bd_nvdimm_is_tech_avail()` treats namespace operations as available except reconfiguration, which requires the `ndctl` utility.
- The file documents the plugin as deprecated since 3.1 and planned for removal in the next major release.

## Data Model
- `BDNVDIMMNamespaceInfo` copy/free helpers manage namespace dev name, mode, size, UUID, sector size, block device, and enabled state.
- Supported public modes include raw, sector, memory, dax, fsdax, devdax, and unknown.
- Compile-time `LIBNDCTL_NEW_MODES` changes how libndctl memory/dax modes map to public fsdax/devdax names.

## Namespace Operations
- `bd_nvdimm_namespace_get_mode_from_str()` and `_get_mode_str()` convert between strings and enum values.
- `bd_nvdimm_namespace_get_devname(device)` maps an active block device name/path to its namespace device name by walking all buses, regions, and namespaces.
- `bd_nvdimm_namespace_enable()` finds a namespace by devname and calls `ndctl_namespace_enable()`.
- `bd_nvdimm_namespace_disable()` calls `ndctl_namespace_disable_safe()`.
- `bd_nvdimm_namespace_info()` returns info for one namespace.
- `bd_nvdimm_list_namespaces()` returns a NULL-terminated array of namespace info for optional bus/region filters and can include idle namespaces.
- `bd_nvdimm_namespace_reconfigure()` shells out to `ndctl create-namespace -e <namespace> -m <mode>` and optionally `-f`.
- `bd_nvdimm_namespace_get_supported_sector_sizes()` returns static supported sector-size arrays by mode.

## Info Extraction
- `get_nvdimm_namespace_info()` detects backing BTT, PFN, and DAX objects.
- Size is taken from BTT/PFN/DAX when those wrappers exist, otherwise from the namespace.
- UUID is pulled from the wrapper object when present; raw namespace UUIDs are treated as absent when null.
- DAX modes intentionally have no block device and sector size 0.
- Non-DAX namespaces default sector size to 512 if libndctl reports 0.

## Filesystem/Storage Relevance
NVDIMM namespaces can expose persistent memory as raw block devices, sector-mode BTT devices, fsdax devices, or devdax character-style memory. This plugin reports and changes namespace presentation modes that affect how filesystems or direct-access applications use persistent memory.
