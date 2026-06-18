# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/Makefile

Builds and installs the `mount.ocfs2` helper.

Key contents:
- Installs program under `$(root_sbindir)`.
- Core source files include `fstab.c`, `mntent.c`, `realpath.c`, `sundries.c`, `xmalloc.c`, and `opts.c`.
- Main source is `mount.ocfs2.c`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, and `aio`.
- Adds optional cluster support libraries for fsdlm and cmap.
- Builds man page `mount.ocfs2.8`.

Research notes:
- This mount helper carries forked/util-linux-style mount support files with OCFS2-specific modifications.
