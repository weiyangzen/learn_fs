## sources/user-network-fs/libtirpc/src/libtirpc.map.in

Purpose: Defines the ELF symbol version map for libtirpc, controlling public ABI, private exports, and conditional symbol insertion.

Important APIs and control flow: `TIRPC_0.3.0` exports core RPC, XDR, auth, client, service, netconfig, pmap, and rpcbind symbols, with placeholders for GSS, DES, and RPC database symbols. Later versions add key/netname APIs (`TIRPC_0.3.2`), local key/publickey hooks and `xdr_sizeof` (`TIRPC_0.3.3`), and selected credential APIs (`TIRPC_1.3.7`). `TIRPC_PRIVATE` exports `__libc_clntudp_bufcreate`, `__svc_clean_idle`, `svc_auth_none`, and `libtirpc_set_debug`.

State and persistence: No runtime state; it shapes link-time and dynamic-loader symbol visibility.

Dependencies and integration: Consumed by the build system, with `@...@` placeholders substituted by configure/meson logic depending on enabled features.

Risks and test signals: ABI regressions occur if symbols move versions or are omitted. Tests should inspect `readelf --dyn-syms --version-info`, build with feature combinations, and verify consumers link against expected versions.
