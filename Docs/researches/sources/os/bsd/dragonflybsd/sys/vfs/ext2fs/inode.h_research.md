# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/inode.h

Defines the incore ext2 inode representation and related inode constants. It bridges ext2 on-disk metadata with DragonFlyBSD vnode state.

`struct inode` contains hash linkage, associated vnode and mount, dirty/state flags, device/inode identity, directory lookup side-effect fields, allocation hints, POSIX metadata, block count, timestamps including nanoseconds and birth time, generation, EA block number, chflags-style flags, direct/indirect block arrays, and an ext4 extent cache.

The direct/indirect layout defines `EXT2_NDADDR` as 12 and `EXT2_NIADDR` as 3. `i_data` overlays all 15 block pointers, while `i_shortlink` and `i_rdev` overlay the same storage for inline symlinks and device nodes.

The header defines ext2-style type and permission constants (`IFREG`, `IFDIR`, `IFLNK`, `ISUID`, `ISGID`, etc.) and inode state flags (`IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`, `IN_RENAME`, `IN_HASHED`, `IN_LAZYMOD`, `IN_SPACECOUNTED`, `IN_LAZYACCESS`). It also defines ext3/ext4 translation flags `IN_E3INDEX` and `IN_E4EXTENTS`.

Kernel-only helpers include `struct indir` for logical block paths, `VTOI` and `ITOV` vnode/inode conversions, and `struct ufid` for NFS file handles.

Important dependencies: used throughout ext2 VFS/vnode/block/dir code. It includes `ext2_extents.h`, so extent-cache state is present even when classic block pointers are used.

Notable risks or research hooks: `i_nlink` is signed `int32_t`, while vnode logic compares it against ext4 link limits. The union overlay between block pointers, symlink data, and device number is central to correct inode type handling.
