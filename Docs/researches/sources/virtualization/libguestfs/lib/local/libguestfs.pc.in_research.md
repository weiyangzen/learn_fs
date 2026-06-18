# File Research: sources/virtualization/libguestfs/lib/local/libguestfs.pc.in

Out-of-tree build pkg-config template for an uninstalled libguestfs tree.

Important behavior:
- Documents that it is a dummy pkg-config file for packages configured against the build tree.
- Points `prefix` and `exec_prefix` at `@abs_top_builddir@`.
- Sets `libdir` to the in-tree `lib/.libs` directory.
- Sets `includedir` to the source tree `include`.
- Emits `Cflags: -I${includedir}` and `Libs: -L${libdir} -lguestfs`.

Filesystem relevance:
- Lets companion tools build against in-tree libguestfs filesystem APIs before installation.
