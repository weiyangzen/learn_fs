# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncinit.c

## Purpose

`ncinit.c` initializes global mapping configuration from the driver service registry parameters and validates the assumptions NameChanger requires before the filter starts.

## Functions

- `NcLoadRegistryString` reads a `REG_SZ` value from a registry key, retrying if the value size changes between length query and data query. It rejects non-strings, empty strings, and strings too large for `UNICODE_STRING`, then copies the non-null-terminated content into nonpaged pool.
- `NcIs8DOT3Compatible` validates configured short names using `RtlIsNameLegalDOS8Dot3`, disallows spaces, tildes, path separators, and lowercase characters, and ensures a long name that is also 8.3-compatible matches the configured short name exactly.
- `NcGetIoOpenDriverRegistryKey` dynamically resolves `IoOpenDriverRegistryKey` via `MmGetSystemRoutineAddress` for OS-version compatibility.
- `NcOpenServiceParametersKey` opens the service `Parameters` key using `IoOpenDriverRegistryKey` when available, otherwise falls back to opening the service registry path then the `Parameters` subkey.
- `NcInitializeMapping` zeroes `NcGlobalData`, opens service parameters, loads `UserMapping`, `UserMappingFinalComponentShort`, and `RealMapping`, splits full mapping paths into parent/final components, rejects paths with adjacent backslashes or invalid roots/final components, and validates the strict short-name assumptions.

## Configuration Contract

Expected registry values are volume-relative absolute paths for user and real mappings plus a user short final component. Paths must start with `\`, include a parent and final component, have no trailing slash final component, and avoid empty path components.

## Integration

The parsed global strings are later used during instance setup in `nc.c`, where volume-specific `NC_MAPPING` structures are built from the configured parent/final component strings.

## Risks and Notes

The sample assumes the real mapping final component is 8.3-compatible and has only one configured real component form. That is explicitly called out as a sample simplification, not a general product-ready mapping model.
