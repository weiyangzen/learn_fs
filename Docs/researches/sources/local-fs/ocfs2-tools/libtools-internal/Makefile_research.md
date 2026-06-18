# File Research: sources/local-fs/ocfs2-tools/libtools-internal/Makefile

Builds the internal helper library `libtools-internal.a`.

Key contents:
- Includes top-level `Preamble.make` and `Postamble.make`.
- Builds `verbose.c`, `progress.c`, `utils.c`, and `scandisk.c`.
- Adds `-fPIC` to `CFLAGS`.
- Defines `VERSION` for compiled code.
- Supports optional debug executables for files containing `DEBUG_EXE`.

Build outputs:
- Uninstalled static library: `libtools-internal.a`.
- Optional debug programs named `debug_<file>` when `OCFS2_DEBUG_EXE` is set.

Research notes:
- This is a private library for shared ocfs2-tools CLI behavior.
- Debug executable discovery is dynamic via `awk` over `$(CFILES)`.
