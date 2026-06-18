<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/configure.ac -->
# sources/user-network-fs/libtirpc/configure.ac

Purpose: Autoconf configuration script for libtirpc feature detection, conditionals, symbol lists, and generated files.

Important APIs, types, and functions: Defines package version 1.3.7, compiler/libtool setup, `LT_VERSION_INFO`, GSSAPI detection, `--enable/disable` flags for gssapi/authdes/ipv6/rpcdb/symvers, symbol substitutions, OS-specific linker flags, header/function/type checks, and output files.

Control flow: Configure evaluates requested features, errors when mandatory GSS dependencies are missing, tests version-script support, populates conditional symbol lists, probes networking constants, and emits Makefiles, version map, config header, and pkg-config file.

State and persistence behavior: Persists results in generated `config.h`, Makefiles, `src/libtirpc.map`, and `libtirpc.pc`.

Dependencies and integration points: Integrates all Automake files and optional source inclusion in `src/Makefile.am`. Depends on krb5-config for GSS and compiler/linker feature probes.

Risks: Defaults enable GSS and IPv6, so minimal systems must pass disable flags. Symbol lists must stay synchronized with implemented APIs. Some feature checks use build OS rather than host, which can matter for cross-compilation.

Test signals: Configure-time checks and successful builds with feature combinations are signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/configure.ac -->
