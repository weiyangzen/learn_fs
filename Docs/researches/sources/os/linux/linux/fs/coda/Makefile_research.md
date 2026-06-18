# File Research: sources/os/linux/linux/fs/coda/Makefile

Build rules for the Linux Coda filesystem module.

Behavior:
- Builds `coda.o` when `CONFIG_CODA_FS` is enabled.
- Core object list: `psdev.o`, `cache.o`, `cnode.o`, `inode.o`, `dir.o`, `file.o`, `upcall.o`, `coda_linux.o`, `symlink.o`, `pioctl.o`.
- Adds `sysctl.o` when `CONFIG_SYSCTL` is enabled.
- Contains commented debug `ccflags-y` line for enabling debug macros.
