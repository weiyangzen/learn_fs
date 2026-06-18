<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/Makefile.am -->
# sources/user-network-fs/libtirpc/src/Makefile.am

Purpose: Automake rules for building the libtirpc shared library and optional source sets.

Important APIs, types, and functions: Defines include flags, `lib_LTLIBRARIES = libtirpc.la`, LDFLAGS/versioning, version-map generation, base source list, conditional AUTH_DES, XDR, SYMVERS, GSS, RPCDB, and key/netname sources.

Control flow: Build generates `libtirpc.map`, compiles base RPC/auth/client/server/XDR sources, appends optional groups based on configure conditionals, and links with GSS libs when enabled.

State and persistence behavior: No runtime persistence; build artifacts include library, map, and objects.

Dependencies and integration points: Driven by configure conditionals. Integrates all authentication files in this subset into the library.

Risks: Conditional source inclusion must match public headers and symbol map. `libtirpc_la_CFLAGS` assignment under GSS can override rather than append other flags if not managed carefully.

Test signals: Successful builds across optional feature combinations are the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/Makefile.am -->
