<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h

Purpose: Public mdssvc client API for connecting to Spotlight metadata service, issuing searches, retrieving results and paths, closing searches, and disconnecting.

Important APIs, types, and functions: Forward declares `mdscli_ctx` and `mdscli_search_ctx`, exposes context helpers, and declares tevent send/recv plus synchronous wrappers for connect, search, get results, get path, close search, and disconnect.

Control flow: No executable logic. The API follows Samba's common async pattern: `*_send()` creates a `tevent_req`, callbacks complete it, `*_recv()` transfers output, and synchronous wrappers block on a private event context.

State and persistence behavior: Context pointers are opaque to callers. `mdscli_close_search_send()` and `mdscli_close_search()` take `struct mdscli_search_ctx **` because successful close consumes/moves the search context.

Dependencies and integration points: Used by RPC client tools and Spotlight search consumers. Requires tevent, dcerpc binding handles, NTSTATUS, and mdssvc generated structures available through surrounding includes.

Risks: Opaque contexts hide the single-operation-at-a-time constraint enforced in synchronous implementations. Callers must not use a search context after passing it to close.

Test signals: Compile coverage for async and sync call sites, ownership tests for close-search pointer consumption, and behavior tests in `cli_mdssvc.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.h -->
