<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/libtirpc.pc.in -->
# sources/user-network-fs/libtirpc/libtirpc.pc.in

Purpose: Pkg-config template for libtirpc consumers.

Important APIs, types, and functions: Defines install paths, name/description/version, `Libs: -L${libdir} -ltirpc`, `Libs.private: @PTHREAD_LIBS@`, and `Cflags: -I${includedir}/tirpc`.

Control flow: Configure substitutes package version and pthread flags; install places the `.pc` file.

State and persistence behavior: No runtime state; installed metadata persists for downstream builds.

Dependencies and integration points: Integrated with top-level Automake pkgconfig install and downstream pkg-config users.

Risks: `Requires` is empty and only pthread appears private; optional GSS/private dependencies may need careful static-link handling depending on build configuration.

Test signals: Validated by downstream configure/pkg-config usage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/libtirpc.pc.in -->
