# File Research: sources/os/linux/linux/block/partitions/aix.c

Implements basic AIX LVM partition discovery for contiguous logical volumes.

Key responsibilities:
- Reads an AIX LVM record from sector 7.
- Supports LVM header version 1.
- Locates VGDA metadata, logical volume descriptors, logical volume names, and physical volume descriptors.
- Reconstructs logical volumes only when their physical partitions are contiguous.
- Emits each contiguous logical volume as a Linux partition.

Important structures:
- `struct lvm_rec` describes the sector-7 LVM record.
- `struct vgda` describes volume group metadata.
- `struct lvd` describes logical volume descriptors.
- `struct lvname` stores names.
- `struct pvd` contains physical partition entries.
- Local `struct lv_info` tracks expected/found physical partitions and contiguity.

Important functions:
- `read_lba()` reads arbitrary byte counts by repeatedly reading 512-byte sectors.
- `alloc_pvd()` and `alloc_lvn()` allocate and load metadata blocks.
- `aix_partition()` is the parser entry point.

Limitations:
- Non-contiguous logical volumes are not emitted and produce warnings.
- Unsupported LVM versions are reported but not parsed.
- The parser is for simple contiguous cases, not full AIX LVM mapping.

Research relevance:
- This is a partition parser that translates an LVM-like foreign metadata layout into plain block partitions when safe.
