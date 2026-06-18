# File Research: sources/windows/reactos/drivers/filesystems/npfs/main.c

## Purpose
Initializes the NPFS driver, device object, dispatch table, fast I/O table, VCB/root DCB, and registry-configured pipe aliases.

## Main Responsibilities
- Defines globals:
  - `NpfsDeviceObject`
  - `NpAliases`
  - `NpAliasList`
  - `NpAliasListByLength`
  - `NpFastIoDispatch`
- Alias support:
  - `NpReadAlias` is an `RtlQueryRegistryValues` callback used twice: first for sizing, then for populating target-name and alias records.
  - `NpCompareAliasNames` performs length-sensitive uppercase lexical comparison.
  - `NpInitializeAliases` reads `Services\Npfs\Aliases`, builds contiguous alias storage, and inserts aliases into sorted linked lists, with short lengths indexed separately.
- `NpFsdDirectoryControl` is unimplemented.
- `DriverEntry`:
  - Initializes aliases.
  - Registers major dispatch routines for create, named-pipe create, close, read/write, information, cleanup, flush, directory control, fsctl, security, and volume info.
  - Installs fast read/write.
  - Creates `\Device\NamedPipe`.
  - Stores the VCB in the device extension and creates the root DCB.

## Important Interactions
- Alias lists are consumed by `create.c`.
- Fast I/O dispatch points to `read.c` and `write.c`.
- VCB initialization and root DCB creation are implemented in `strucsup.c`.

## Risks / Review Notes
- Directory control is explicitly unimplemented.
- Alias storage is one contiguous allocation containing `UNICODE_STRING`, `NPFS_ALIAS`, and string payloads; pointer arithmetic correctness is important.
- On `IoCreateDevice` failure after alias initialization, alias memory is not freed.
