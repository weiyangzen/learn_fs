# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/Makefile

This makefile builds an internal PIC `libblkid-internal.a` only when system blkid support is unavailable. It compiles legacy blkid implementation files for cache, devices, names, probing, reading, resolving, tags, and version handling.

It defines config-style preprocessor symbols for available headers and `lseek64`, includes the parent console directory, and distributes blkid headers/source plus ChangeLog. This is a compatibility vendored blkid for `ocfs2console`.
