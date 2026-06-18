# File Research: sources/virtualization/nbdkit/plugins/cdi/Makefile.am

This Automake file builds `nbdkit-cdi-plugin.la` only on non-Windows platforms because the implementation runs a shell script. It compiles `cdi.c` with public/generated headers, common include files, common utilities, and local include path support.

The module links common utilities, the platform import library, and `$(JANSSON_LIBS)`, with `$(JANSSON_CFLAGS)` in compile flags. Although this file links Jansson, the listed `cdi.c` uses shell tools such as `jq` rather than direct JSON parsing. Optional plugin symbol versioning uses `plugins/plugins.syms`.

POD-enabled builds generate `nbdkit-cdi-plugin.1` and HTML documentation, inserting the shared magic-parameter text.
