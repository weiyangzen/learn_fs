# File Research: sources/os/linux/linux/fs/nilfs2/cpfile.h

This header declares the checkpoint-file API used by mount, snapshot, cleaner, ioctl, and root-loading paths.

Declared capabilities:
- Read a checkpoint into a root/ifile pair.
- Create and finalize checkpoints.
- Delete a single checkpoint or a range of checkpoints.
- Change checkpoint mode between checkpoint and snapshot.
- Test whether a checkpoint is a snapshot.
- Return checkpoint statistics and checkpoint/snapshot info arrays.
- Read or get the cpfile inode from the on-disk raw inode.

Important role:
- This is the public boundary for all cpfile manipulation; callers do not access checkpoint entries directly.
- The header exposes `nilfs_cpstat` and on-disk checkpoint/inode dependencies through NILFS UAPI and ondisk headers.
