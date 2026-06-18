<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am

## Purpose

This Automake file builds the bundled `rpcgen` RPC protocol compiler and installs its manual page.

## Important APIs, Types, and Functions

It declares `bin_PROGRAMS = rpcgen`, `man_MANS = rpcgen.1`, `noinst_HEADERS = proto.h rpc_parse.h rpc_scan.h rpc_util.h`, and compiles all `rpc_*.c` generator, parser, scanner, and utility sources. It links with `$(LIBINTL)`.

## Control Flow

Automake compiles the scanner/parser, main driver, output generators, and shared utilities into one `rpcgen` binary. `CLEANFILES = *~` removes editor backups.

## State and Persistence Behavior

No runtime state exists in the build file. It controls installed compiler/manual artifacts.

## Dependencies and Integration Points

It integrates the ONC RPC code generator with nfs-utils and depends on intl support when configured.

## Risks and Edge Cases

Generated build rules must compile older C code with modern compiler warnings and headers. `EXTRA_DIST=${MANS}` appears to use `MANS`, while the file declares `man_MANS`; build tooling should verify distribution contents.

## Test Signals

Build tests should compile `rpcgen`, install the binary and man page, and run smoke generation for a small `.x` file covering header, XDR, client, server, and table outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/Makefile.am -->
