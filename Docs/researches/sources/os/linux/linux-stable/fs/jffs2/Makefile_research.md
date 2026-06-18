# File Research: sources/os/linux/linux-stable/fs/jffs2/Makefile

## Scope
Defines the JFFS2 kernel object composition.

## Build Behavior
`obj-$(CONFIG_JFFS2_FS) += jffs2.o` builds the aggregate module/built-in object. Core files include compression dispatch, directory/file/ioctl, node management, allocation, read/write, scanning, garbage collection, symlink, build, erase, background GC, filesystem/superblock, debug, and writev support.

Conditional objects add write-buffering, xattr handlers, trusted/user/security xattrs, POSIX ACLs, individual compressors, and summary support according to Kconfig symbols.

## Dependencies
Directly mirrors feature gates from `Kconfig`.

## Risks And Invariants
Feature-specific source files are only linked when their config dependencies are enabled; callers must use config stubs or guards for optional ACL/xattr/compressor behavior.
