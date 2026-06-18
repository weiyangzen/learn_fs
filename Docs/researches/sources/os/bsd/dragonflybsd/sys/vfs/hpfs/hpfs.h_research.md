# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs.h

Source read: complete file, 405 lines.

Purpose: Main HPFS internal header. It declares on-disk structures, mount/node in-memory structures, allocation-tree helpers, directory-entry macros, codepage structures, debug/malloc declarations, vnode conversion macros, and hash-cache prototypes.

Key on-disk structures:
- `sublock` and `spblock` model HPFS super and spare blocks, including magic values, root fnode, total sectors, bad blocks, bitmap pointers, dirblock band metadata, hotfix/spare dirblock fields, and codepage index pointers.
- `hpfsdirent` and `dirblk` describe directory B+tree records and 2 KiB directory blocks, including down-pointer handling through `DE_DOWNLSN()`.
- `alblk`, `alleaf`, `alnode`, and `alsec` describe HPFS allocation trees: leaves map logical offsets to physical extents, nodes point to allocation sectors, and sectors store nested allocation blocks.
- `fnode` stores file metadata, parent pointer, embedded allocation block, size, EA metadata, and inline data.
- `ea`, `cpiblk`, `cpisec`, `cpdblk`, and `cpdsec` describe extended attribute and codepage data.

Key in-memory structures:
- `hpfsmount` stores copied super/spare blocks, export state, device vnode/device id, ownership/mode defaults, bitmap index/data, codepage conversion tables, free-block count, and data-band count.
- `hpfsnode` stores vnode-private state, copied fnode, device references, owner/mode, flags, cached parent directory timestamps, and cached name.
- `hpfid` overlays `struct fid` for NFS file handles.

Integration:
- `VFSTOHPFS()`, `VTOHP()`, and `HPTOV()` connect VFS/vnode objects to HPFS private structures.
- Declares hash routines implemented in `hpfs_hash.c`.
- Shared by all HPFS C files.

Risks and review notes:
- Many structures are direct on-disk overlays and assume exact layout, alignment, and endian behavior.
- Directory and allocation macros perform pointer arithmetic against variable-length records; malformed media can drive out-of-bounds access unless all callers validate record lengths.
- `H_INVAL`, `H_CHANGE`, and `H_PARCHANGE` govern lazy writeback and reclaim behavior; missed flag updates can lose metadata.
