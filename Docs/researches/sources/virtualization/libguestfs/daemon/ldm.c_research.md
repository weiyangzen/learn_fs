# File Research: sources/virtualization/libguestfs/daemon/ldm.c

Wraps `ldmtool` for Windows Logical Disk Manager metadata.

Important behavior:
- `optgroup_ldm_available` checks for `ldmtool`.
- Exposes create/remove all, scan, scan selected devices, diskgroup name/volumes/disks, and volume type/hint/partitions.
- Parses `ldmtool` JSON output with json-c strict and UTF-8 validation.
- Converts JSON arrays of strings and object string fields into daemon protocol return values.
- Handles JSON null-to-empty for volume hints.

Filesystem relevance: discovers and activates Windows dynamic disk volume topology.
