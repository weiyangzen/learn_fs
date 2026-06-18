# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fsid.h

## Role

Defines legacy filesystem type-name constants used in filesystem information structures and user-level mapping of filesystem type names to indexes.

## Key Definitions

String constants:
- `S51K`
- `PROC`
- `DUFST`
- `NFS`
- `S52K`

## Semantics

Comments state these names must remain constant across releases because user-level routines map filesystem type names to indices such as `ip->i_fstyp`, supporting programs like `mount`.

## Risk Notes

Although small and legacy, these constants are ABI names. Renaming or removing them can break userland tools that depend on stable filesystem type strings.
