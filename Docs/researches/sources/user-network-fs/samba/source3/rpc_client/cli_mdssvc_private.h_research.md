<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h

Purpose: Private mdssvc client state header shared by `cli_mdssvc.c` and `cli_mdssvc_util.c`.

Important APIs, types, and functions: Defines `struct mdsctx_id`, `struct mdscli_ctx`, and `struct mdscli_search_ctx`. The main context stores RPC binding/policy state, async counter, context ids, fragment size, device/flags, command-specific fields, share path, and path scope. The search context stores parent context, query context id, unique query id, live flag, scope, and query string.

Control flow: No executable logic. These structs are populated by connect/search helpers and read by blob builder functions.

State and persistence behavior: `mdscli_ctx` is the durable connection/session object; `mdscli_search_ctx` is durable per open query. `ctx_id.id` increments for new logical commands while `ctx_id.connection` identifies the tree connection. Fixed-size `share_path[1025]` stores the server-returned base path.

Dependencies and integration points: Included only by mdssvc client internals. It couples command blob construction, RPC call state, and response validation through shared fields such as `dev`, `flags`, `mdscmd_open.unkn2`, `path_scope_len`, and `share_path_len`.

Risks: The structure documents several fields as unknown; protocol changes can break assumptions. Fixed-size share path storage requires strict length validation in connect. Exposing mutable internals across two C files makes ordering dependencies easy to miss.

Test signals: Compile checks for internal users, connect tests that validate share/path length bounds, and protocol regression tests covering unknown fields across server versions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_private.h -->
