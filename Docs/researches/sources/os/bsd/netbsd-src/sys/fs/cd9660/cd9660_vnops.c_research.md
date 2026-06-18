# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vnops.c

Read completely: 924 lines.

Implements cd9660 vnode operations for access checks, attributes, reads, directory iteration, symlink reads, block strategy, pathconf, and limited setattr behavior. Operation tables are provided for regular cd9660 vnodes plus special-device and FIFO vnodes.

Access is read-only for directories, regular files, and symlinks; write is only allowed to pass through resident socket/fifo/device style nodes where the generic vnode layer supports it. Permission checks apply mount-supplied uid/gid overrides and file/directory masks before delegating to kauth/genfs.

Regular file reads use UBC with read advice, while non-regular paths use buffer reads and readahead. `cd9660_readdir()` walks ISO directory records block by block, validates record sizes and block boundaries, translates names through RRIP or ISO/Joliet helpers, synthesizes `.`/`..`, handles associated file ordering in default ISO mode, and returns cookies when requested.

`cd9660_readlink()` rereads the directory record containing the symlink inode and extracts RRIP `SL` content. `cd9660_strategy()` maps logical blocks through `VOP_BMAP` before forwarding to the device vnode. `cd9660_setattr()` rejects all attribute changes except size changes for device/fifo vnode cases.
