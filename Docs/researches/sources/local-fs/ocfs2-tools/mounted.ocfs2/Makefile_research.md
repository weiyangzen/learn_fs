# File Research: sources/local-fs/ocfs2-tools/mounted.ocfs2/Makefile

Build recipe for `mounted.ocfs2`.

It builds one sbin program from `mounted.c`, installs the `mounted.ocfs2.8` man page, and links against `libocfs2`, `libo2dlm`, `libo2cb`, `libtools-internal`, com_err, UUID, AIO, and optional DLM/CMAP libraries.
