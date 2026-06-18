# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.h

Declares the private NILFS helper and vnode-operation interface shared by `nilfs_subr.c`, `nilfs_vfsops.c`, and `nilfs_vnops.c`.

Key contents:
- `VFSTONILFS()` mount-data cast macro.
- Prototypes for segment arithmetic, metadata layout calculation, CRC, segment-log reading, super-root search, block reading, btree lookup, and DAT translation.
- Prototypes for raw node lifecycle, time/update/resize helpers, directory lookup/create/delete/attach/detach helpers.
- Prototypes for all NILFS vnode operations exported by `nilfs_vnops.c`.

Role:
- This header is the internal NILFS subsystem contract.
- It exposes many mutation-oriented operations even though the corresponding implementations currently return `EROFS` or are stubs.
