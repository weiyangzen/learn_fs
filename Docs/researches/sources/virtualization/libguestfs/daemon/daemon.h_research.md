# File Research: sources/virtualization/libguestfs/daemon/daemon.h

Main shared header for C daemon modules.

Key points:
- Declares global daemon state, sysroot helpers, xread/xwrite, stringsbuf utilities, mountable handling, protocol reply functions, FileIn/FileOut transfer functions, progress APIs, and many cross-file helper APIs.
- Defines `mountable_t` and `stringsbuf`.
- Declares optional group table structure and generated dispatch interfaces.
- Provides `NEED_ROOT`, `ABS_PATH`, `CHROOT_IN`, and `CHROOT_OUT` macros.
- Error macros normalize protocol replies and unavailable feature reporting.
- Exposes filesystem-specific helpers used across modules, including ext, Btrfs, XFS, NTFS, swap, blkid, LVM, xattrs, debug-bmap, Augeas, hivex, and journal finalizers.
- Documents important chroot constraints: match enter/exit paths, keep cwd `/`, use absolute paths, and preserve `errno`.
