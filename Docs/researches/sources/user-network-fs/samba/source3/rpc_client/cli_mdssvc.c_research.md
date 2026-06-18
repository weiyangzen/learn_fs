<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c

Purpose: Implements asynchronous and synchronous client helpers for Samba's Spotlight/metadata server (`mdssvc`) RPC interface.

Important APIs, types, and functions: Exports `mdscli_new_ctx_id()`, `mdscli_get_basepath()`, connect/search/results/path/close/disconnect send-recv-sync triplets, and `mdscli_search_get_ctx()` through the header. State machines are represented by per-operation `*_state` structs and callbacks such as `mdscli_connect_open_done()`, `mdscli_connect_fetch_props_done()`, `mdscli_search_cmd_done()`, `mdscli_get_results_cmd_done()`, `mdscli_get_path_done()`, `mdscli_close_search_done()`, and `mdscli_disconnect_done()`.

Control flow: Connect opens mdssvc, sends an unknown setup call, fetches server properties, unpacks the Spotlight blob, and records path scope. Search builds an open-query blob, sends it, and expects a zero result token. Get-results sends a fetch-results blob, follows response fragments until the fragment id is zero, unpacks accumulated data, validates status, CNID container fields, and context, and returns a NULL-terminated-by-size talloc array of CNIDs. Get-path requests `kMDItemPath` for a CNID, unpacks a nested response path, strips the stored path-scope/share-path prefix, and returns a relative path. Close-search and disconnect send the corresponding close commands. Synchronous wrappers create a temporary tevent context, reject calls while `async_pending` is nonzero, poll the async request, and receive results.

State and persistence behavior: `mdscli_ctx` stores the binding handle, policy handle, generated context ids, max fragment size, device/flags, command scratch fields, share path, path scope, and an `async_pending` counter. `mdscli_search_ctx` stores query context id, unique id, live flag, scope, and query string. Contexts are talloc-owned and moved to caller contexts on successful recv calls.

Dependencies and integration points: Depends on generated `ndr_mdssvc_c` client stubs, tevent request helpers, Spotlight dalloc/marshalling helpers, and blob builders from `cli_mdssvc_util.c`. It is the client-side companion to Samba's mdssvc RPC server and Spotlight query tooling.

Risks: The code is tightly coupled to undocumented mdssvc blob shapes and magic constants such as connection id `0x6b000060`, CNID marker `0xadd`, and "search in progress" status `35`. Path prefix stripping assumes server path format and validated scope lengths. `async_pending` protects synchronous wrappers from overlapping use, but async callers must still sequence shared context operations carefully. Fragment accumulation guards integer overflow but can still allocate large server-controlled responses up to available memory.

Test signals: Tests should simulate mdssvc RPC responses for successful connect/search/results/path/close/disconnect, fragmented result streams, search-in-progress with no CNIDs, no-more-matches, bad path-scope values, bad CNID context or marker, malformed dalloc blobs, overlapping synchronous calls, and path prefix edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc.c -->
