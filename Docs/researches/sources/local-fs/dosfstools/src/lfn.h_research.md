# File Research: sources/local-fs/dosfstools/src/lfn.h

Public interface for VFAT long-filename handling.

Declared functions:
- `lfn_reset()`
- `lfn_add_slot()`
- `lfn_get()`
- `lfn_check_orphaned()`
- `lfn_fix_checksum()`

Role:
- Lets `check.c` stream directory entries through an LFN state machine and repair malformed LFN metadata.
