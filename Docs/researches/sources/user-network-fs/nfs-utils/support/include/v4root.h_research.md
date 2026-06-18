# sources/user-network-fs/nfs-utils/support/include/v4root.h

## Purpose
Declares dynamic NFSv4 pseudo-root support.

## Important APIs, Types, and Functions
Extern `v4root_needed` and `v4root_set()`.

## Control Flow
After etab/export parsing, callers invoke `v4root_set()` when pseudo-root generation may be needed.

## State and Persistence Behavior
`v4root_needed` is global process state set by etab reading. Generated pseudo exports enter the export list.

## Dependencies and Integration Points
Implemented by `support/export/v4root.c` and used by `xtab.c`/export setup.

## Risks and Edge Cases
Global flag ordering matters; calling before export list population has no effect.

## Test Signals
Test etab fsid0 detection and pseudo-root creation paths.
