# File Research: sources/virtualization/libnbd/lib/local/libnbd.pc.in

Build-tree pkg-config template for out-of-tree packages using an uninstalled libnbd tree.

Content:
- Sets prefix/exec_prefix to `@abs_top_builddir@`.
- Points `libdir` at `lib/.libs`.
- Points `includedir` at source `include`.
- Emits `Cflags: -I${includedir}` and `Libs: -L${libdir} -lnbd`.

Research notes:
- This is intentionally a dummy local development pkg-config file.
- Comments note that the project `./run` script handles `PKG_CONFIG_PATH`.
