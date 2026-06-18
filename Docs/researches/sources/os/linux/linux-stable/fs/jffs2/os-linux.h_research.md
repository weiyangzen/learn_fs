# File Research: sources/os/linux/linux-stable/fs/jffs2/os-linux.h

This header is the Linux OS adaptation layer for JFFS2 core code.

Key responsibilities:
- Maps JFFS2 private structures to Linux `inode` and `super_block` objects through `JFFS2_INODE_INFO()`, `OFNI_EDONI_2SFFJ()`, `JFFS2_SB_INFO()`, and `OFNI_BS_2SFFJ()`.
- Exposes inode metadata macros for size, mode, uid, gid, rdev, and clamped 32-bit atime/mtime/ctime values.
- Defines `sleep_on_spinunlock()` for wait-queue sleep while dropping a spinlock.
- Initializes per-inode JFFS2 state in `jffs2_init_inode_info()`.
- Provides read-only detection and sector address helpers.
- Supplies no-op/direct-MTD macro implementations when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Declares write-buffer, NAND, DataFlash, UBI volume, and NOR write-buffer setup/read/write helpers when write-buffer support is enabled.
- Declares Linux-facing JFFS2 operations and helpers implemented across `background.c`, `dir.c`, `file.c`, `ioctl.c`, `fs.c`, `symlink.c`, and `writev.c`.

Important interactions:
- Controls whether core code sees direct `mtd_read`/`mtd_writev` behavior or the write-buffered wrappers from `wbuf.c`.
- Summary support changes `jffs2_can_mark_obsolete()`: with summaries enabled, nodes cannot be physically marked obsolete even without write buffering.
- The header is included by most JFFS2 implementation files and defines much of the OS-specific contract.

Notable invariants and risks:
- Time values are clamped into 32-bit on-flash fields.
- Write-buffer-disabled builds intentionally stub many NAND/OOB/bad-block operations.
- `SECTOR_ADDR(x)` depends on the caller having a visible `c` superblock-info variable.
