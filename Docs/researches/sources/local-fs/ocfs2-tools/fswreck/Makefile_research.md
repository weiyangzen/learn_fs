# File Research: sources/local-fs/ocfs2-tools/fswreck/Makefile

This Makefile builds the `fswreck` test utility, a deliberately destructive OCFS2 corruption injector used to exercise `fsck.ocfs2`.

Key build content:
- Includes top-level `Preamble.make` and `Postamble.make`.
- Defines `UNINST_PROGRAMS = fswreck`, so the utility is built but not installed as a normal public program.
- Compiles corruption modules for chains, extents, groups, inodes, local alloc, truncate logs, special files, symlinks, directories, journals, quotas, refcounts, and discontiguous block groups.
- Exports matching headers under `include/`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, GLib, com_err, and AIO libraries.
- Conditionally links `-ldlm_lt` when `BUILD_FSDLM_SUPPORT` is enabled.

Integration notes:
- The source list mirrors the corruption dispatch table in `main.c`.
- `dist-subdircreate` ensures the distribution include directory exists.
