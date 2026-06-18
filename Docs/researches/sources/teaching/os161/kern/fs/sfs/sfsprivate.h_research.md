# File Research: sources/teaching/os161/kern/fs/sfs/sfsprivate.h

Private SFS header tying together internal modules.

Contents:
- Declares exported vnode ops tables `sfs_fileops` and `sfs_dirops`.
- Defines `SFSUIO`, a helper macro for initializing a kernel `uio` for one filesystem block at `block * SFS_BLOCKSIZE`.
- Declares internal functions for block allocation, block mapping/truncation, directory lookup/link/unlink, inode lifecycle, block/file/metadata I/O, and root vnode loading.

Role:
- Centralizes internal cross-file contracts for SFS implementation files.
- Keeps public SFS structures in `<sfs.h>` and on-disk ABI in `<kern/sfs.h>`.
