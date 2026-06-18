# File Research: sources/virtualization/nbdkit/plugins/tcl/Makefile.am

Builds the Tcl language plugin when `HAVE_TCL` is enabled.

Key behavior:
- Distributes `nbdkit-tcl-plugin.pod` and `example.tcl`.
- Builds `nbdkit-tcl-plugin.la` from `tcl.c` and the public plugin header.
- Adds include paths for source/build `include`.
- Uses `$(TCL_CFLAGS)` and `$(TCL_LIBS)` for Tcl integration.
- Links as a libtool module with `-module -avoid-version -shared` and Windows no-undefined/import-library support.
- Adds the shared plugin linker version script when `USE_LINKER_SCRIPT` is set.
- Builds `nbdkit-tcl-plugin.3` from POD documentation when `HAVE_POD` is enabled.

Dependencies:
- Automake/libtool.
- Tcl headers and libraries discovered by configure.
- `podwrapper.pl` for manpage/html generation.
