# File Research: sources/os/linux/linux/fs/jffs2/os-linux.h

## Role

Linux OS adaptation header for JFFS2 core code. It maps JFFS2 internal objects to Linux VFS objects and hides write-buffer configuration differences behind macros/prototypes.

## Key Responsibilities

- Defines conversions between `struct inode`/`struct super_block` and JFFS2 private structures.
- Exposes inode field macros for size, mode, uid, gid, rdev, and clamped 32-bit atime/mtime/ctime values.
- Provides `sleep_on_spinunlock()` for wait-queue sleep while dropping a spinlock.
- Initializes per-inode JFFS2 state in `jffs2_init_inode_info()`.
- Defines read-only and sector-address helpers.
- Provides direct-MTD no-op stubs when `CONFIG_JFFS2_FS_WRITEBUFFER` is disabled.
- Declares write-buffer, NAND, DataFlash, UBI, and NOR write-buffer helpers when write-buffer support is enabled.
- Declares Linux-facing operations implemented by background, dir, file, ioctl, fs, symlink, and writev code.

## Important Interactions

- Controls whether callers use direct `mtd_read`/`mtd_writev` or buffered wrappers from `wbuf.c`.
- Defines `jffs2_can_mark_obsolete()`, which is disabled when summary support is enabled and otherwise depends on flash bit-writability.
- Exposes `jffs2_flash_writev()` and `jffs2_flash_read()` as the common I/O interface used by scan, read, write, and summary paths.

## Invariants and Risks

- On-flash timestamps are clamped to `U32_MAX`.
- `SECTOR_ADDR(x)` depends on a visible local variable named `c`.
- Write-buffer-disabled builds intentionally stub NAND/OOB/bad-block behavior.
