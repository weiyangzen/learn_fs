# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dinode.h

Read completely: 133 lines.

Defines the 128-byte EFS on-disc inode format. `struct efs_dinode` stores mode, link count, 16-bit uid/gid, byte size, access/modify/change times, generation, extent count, version, and a union for direct/indirect extents, inline symlink content, or special-device numbers.

The inode supports twelve direct extent descriptors in `di_extents`. When `di_numextents` exceeds `EFS_DIRECTEXTENTS`, these descriptors identify indirect extent blocks, with the first descriptor’s offset carrying the indirect extent count. Zero-extent symlinks can store the target inline in the union.

The header defines root inode number, inode size/count per basic block, old/new device-number extraction macros, and EFS file type/permission constants corresponding to IRIX on-disc mode bits.
