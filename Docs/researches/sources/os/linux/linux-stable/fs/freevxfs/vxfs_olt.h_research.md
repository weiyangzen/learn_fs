# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_olt.h

This header defines VxFS Object Location Table constants and record structures.

Major responsibilities:
- Define the OLT magic number.
- Enumerate OLT record types: free, fileset header, current usage table, inode list, device config, and superblock/log/OLT inode records.
- Declare the OLT header structure.
- Declare common, free, inode-list, current-usage-table, superblock/log, device, and fileset-header OLT entry formats.

Important design points:
- The OLT is a metadata directory for locating filesystem-wide internal objects.
- FreeVxFS uses only a subset of OLT records during mount, mainly fileset header and initial inode-list records.
- Replica fields are represented in the structures, but the implementation uses the primary entries.

Key invariants:
- Every variable OLT record begins with type and size fields compatible with `struct vxfs_oltcommon`.
- All fields are on-disk endian and require `fs32_to_cpu()` before use.
- OLT parsing depends on valid `olt_size` fields to advance through the extent.

External interfaces:
- Used by `vxfs_olt.c`.
