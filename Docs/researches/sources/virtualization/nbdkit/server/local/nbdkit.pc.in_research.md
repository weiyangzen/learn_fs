# File Research: sources/virtualization/nbdkit/server/local/nbdkit.pc.in

Purpose: Template for a local-build `pkg-config` file used to compile plugins against an uninstalled nbdkit build tree.

Fields:
- `prefix` and `exec_prefix` point at `@abs_top_builddir@`.
- `Name`, `Version`, and `Description` describe nbdkit.
- `Requires` is empty.
- `Cflags` includes both source and build include directories.
- `Libs` is empty.

Design implication:
- Plugins compiled locally include headers from the source/build tree but do not link against a separate nbdkit library; symbols are provided by the server process at load time.
