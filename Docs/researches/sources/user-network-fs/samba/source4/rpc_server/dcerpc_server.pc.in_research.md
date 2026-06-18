# sources/user-network-fs/samba/source4/rpc_server/dcerpc_server.pc.in

Purpose: pkg-config template for the DCE/RPC server library.

Important fields and flow: defines `prefix`, `exec_prefix`, `libdir`, `includedir`, and `modulesdir` substitution variables; names the package `dcerpc_server`; declares dependency `Requires: dcerpc`; emits `Version: @PACKAGE_VERSION@`; and links with `@LIB_RPATH@ -L${libdir} -ldcerpc-server`.

State and persistence: build-time metadata only. It is transformed by the build system into a `.pc` file consumed by downstream builds.

Dependencies and integration: coordinates external or internal consumers that need the DCE/RPC server library and modules directory.

Risks and test signals: stale library names or missing `Requires` entries break consumers at compile/link time. Build tests should validate pkg-config output after configure substitution and confirm `Libs` resolves the built shared library.
