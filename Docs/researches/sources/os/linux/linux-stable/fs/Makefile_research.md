# File Research: sources/os/linux/linux-stable/fs/Makefile
- Purpose: Top-level build manifest for Linux filesystem and VFS code.
- Core build: Always builds VFS core objects such as open/read-write/file-table/super/inode/dcache/namei/stat/namespace/splice/sync/attr and related infrastructure.
- Conditional build: Adds filesystems and subsystems according to `CONFIG_*` symbols, including `9p/`, `adfs/`, and `affs/`.
- Integration: Maps top-level Kconfig selections to compiled directories and object files.
- Research notes: Ordering matters for some entries, such as hfsplus before hfs; this file is the build-level counterpart to `fs/Kconfig`.
