# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.c

## Scope

Implements Rock Ridge Interchange Protocol and SUSP parsing for CD9660: POSIX attributes, special devices, alternate names, relocated directories, symbolic links, timestamps, continuation areas, and extension-reference validation.

## APIs And Behavior

- `cd9660_rrip_analyze()` parses `PX`, `TF`, `PN`, `RR`, `CE`, and `ST` records to populate an `iso_node`.
- `cd9660_rrip_getname()` extracts Rock Ridge `NM` names and handles `CL`, `PL`, and `RE` relocated-directory records.
- `cd9660_rrip_getsymname()` reconstructs symbolic link targets from `SL` component records.
- `cd9660_rrip_offset()` validates root `SP` and `ER` records, handles CD-ROM XA skip padding, and returns the SUSP skip count.
- `cd9660_rrip_loop()` is the central scanner: it locates system-use fields after the ISO filename, applies mount-specific root skip offsets, dispatches records through `RRIP_TABLE`, follows `CE` continuation areas, and runs default attribute/name/timestamp handlers for missing expected fields.

## Dependencies

Depends on `iso.h` layout/numeric helpers, RRIP record structs from `cd9660_rrip.h`, analysis state from `iso_rrip.h`, buffer I/O, mount state, hostname, and namecache full-path logic for volume-root symbolic-link components.

## Risks And Invariants

Continuation records are bounded against `volume_space_size` and `logical_block_size`; malformed lengths stop scanning. Name and symlink assembly must honor `NAME_MAX`/`MAXPATHLEN`, continuation flags, and component ordering. Missing `PX` or `TF` records fall back to ISO defaults, but malformed long names are treated as absent.
