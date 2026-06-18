# File Research: sources/os/linux/linux/fs/nilfs2/ifile.h

This header declares the NILFS2 inode-file API and provides raw inode mapping helpers.

Key contents:
- `nilfs_ifile_map_inode()` calculates the palloc entry offset for an inode number and maps the containing folio locally.
- `nilfs_ifile_unmap_inode()` unmaps the local mapping.
- Declares create/delete/get inode block functions.
- Declares free-inode counting.
- Declares `nilfs_ifile_read()` for loading the ifile for a root/checkpoint.

Important role:
- This header is the safe access point for raw on-disk inode entries stored inside the ifile metadata file.
- It keeps callers from duplicating palloc offset arithmetic.
