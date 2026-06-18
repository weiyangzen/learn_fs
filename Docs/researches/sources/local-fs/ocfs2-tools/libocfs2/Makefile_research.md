# File Research: sources/local-fs/ocfs2-tools/libocfs2/Makefile

Builds `libocfs2.a`, the core OCFS2 userspace library. It includes top-level build preamble/postamble files, sets `INCLUDES = -I$(TOPDIR)/include`, and compiles with `-fPIC`.

The source list covers allocation, bitmaps, metadata checks, block typing, cached inodes, chain allocators, directory handling, extents, I/O, quota, xattrs, refcounting, indexed directories, and related helpers. Headers distributed from this directory include `bitmap.h`, `crc32table.h`, `dir_iterate.h`, `dir_util.h`, extent/refcount headers, and generated `ocfs2_err.h`.

Conditional behavior: if `BUILD_FSDLM_SUPPORT` is set, libo2cb links with `-ldlm_lt`; if `OCFS2_DEBUG_EXE` is set, files containing `DEBUG_EXE` can be built into `debug_*` standalone programs linked against `libocfs2.a`, `libo2dlm`, and `libo2cb`.

Generated files: `compile_et ocfs2_err.et` produces `ocfs2_err.c` and `ocfs2_err.h`. `clean-err` removes those generated error-table files.
