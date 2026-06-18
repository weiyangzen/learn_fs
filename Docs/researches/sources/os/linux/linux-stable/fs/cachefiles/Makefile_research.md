# File Research: sources/os/linux/linux-stable/fs/cachefiles/Makefile

This Makefile builds the CacheFiles module.

Core object list:
- `cache.o`
- `daemon.o`
- `interface.o`
- `io.o`
- `key.o`
- `main.o`
- `namei.o`
- `security.o`
- `volume.o`
- `xattr.o`

Optional object list:
- `error_inject.o` when `CONFIG_CACHEFILES_ERROR_INJECTION=y`
- `ondemand.o` when `CONFIG_CACHEFILES_ONDEMAND=y`

Build target:
- `obj-$(CONFIG_CACHEFILES) := cachefiles.o`

The layout matches the subsystem split: module setup in `main.c`, daemon device protocol in `daemon.c`, FS-Cache hooks in `interface.c`, VFS object lookup in `namei.c`, netfs I/O operations in `io.c`, coherency xattrs in `xattr.c`, volume management in `volume.c`, and security credential handling in `security.c`.
