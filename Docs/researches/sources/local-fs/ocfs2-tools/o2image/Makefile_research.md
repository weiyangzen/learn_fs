# File Research: sources/local-fs/ocfs2-tools/o2image/Makefile

Build recipe for `o2image`.

It enables strict C warnings, builds the `o2image` sbin program from `o2image.c`, installs `o2image.8`, includes GLib flags, defines `VERSION`, and links against GLib, `libocfs2`, com_err, and AIO. It declares O2CB/O2DLM variables, but the explicit link rule only uses the libocfs2-side dependencies.
