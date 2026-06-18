<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h

Purpose: Internal/public boundary header for mdssvc request blob builders.

Important APIs, types, and functions: Declares blob builders for fetch properties, open search, get results, get path, and close search. Each fills a `struct mdssvc_blob` from an mdssvc connection or search context.

Control flow: No executable logic. The builders are called before sending mdssvc command RPCs.

State and persistence behavior: No header-owned state. Blob lifetime is controlled by the memory context passed to the implementation.

Dependencies and integration points: Included by `cli_mdssvc.c` and implemented by `cli_mdssvc_util.c`. It depends on opaque mdssvc client context types and generated `mdssvc_blob`.

Risks: Callers must pass initialized private contexts with valid fragment size, context ids, path scope, and query fields; the header does not enforce those invariants.

Test signals: Compile coverage and blob-shape tests through `cli_mdssvc_util.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.h -->
