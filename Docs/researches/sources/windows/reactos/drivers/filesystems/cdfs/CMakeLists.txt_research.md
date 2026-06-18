# File Research: sources/windows/reactos/drivers/filesystems/cdfs/CMakeLists.txt

## Scope And Purpose

`CMakeLists.txt` defines the ReactOS CDFS kernel-mode filesystem driver build.

Complete file read: 41 lines.

## Build Behavior

- Adds ReactOS driver include directories.
- Defines the CDFS source list, including allocation, cache, initialization, create/cleanup/close, directory, file info, fsctl, read/write, PnP, resource, verification, volume info, and work queue modules.
- Builds `cdfs` as a module library with `cdfs.rc`.
- Marks the target as a kernel-mode driver with `set_module_type(cdfs kernelmodedriver)`.
- Links against `${PSEH_LIB}` and `memcmp`.
- Imports `ntoskrnl` and `hal`.
- Installs the driver under `reactos/system32/drivers`.
- Registers `cdfs_reg.inf`.

## Integration Points

This file is the build entry for `sources/windows/reactos/drivers/filesystems/cdfs`. It wires the CDFS driver into the ReactOS build, driver packaging, and registry INF installation.

## Notes

The source list is explicit; adding a CDFS module requires updating this file unless another build file includes it indirectly.
