<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c

Purpose: Builds packed Spotlight/dalloc request blobs used by the mdssvc client operations.

Important APIs, types, and functions: Exports `mdscli_blob_fetch_props()`, `mdscli_blob_search()`, `mdscli_blob_get_results()`, `mdscli_blob_get_path()`, and `mdscli_blob_close_search()`. It constructs `DALLOC_CTX`, `sl_array_t`, `sl_dict_t`, and `sl_cnids_t` trees and serializes them with `sl_pack_alloc()`.

Control flow: Each helper allocates a root dalloc context, creates the nested command array expected by mdssvc, appends a selector string such as `fetchPropertiesForContext:`, `openQueryWithParams:forContext:`, `fetchQueryResultsForContext:`, `fetchAttributes:forOIDArray:context:`, or `closeQueryForContext:`, fills context ids and command-specific dictionaries/arrays, packs the tree into an `mdssvc_blob`, frees the temporary dalloc tree, and returns NTSTATUS. The search blob includes query timing/count parameters, a unique id, `kMDItemFSName`, the query string, and scope array. The get-path blob requests `kMDItemPath` for one CNID.

State and persistence behavior: No module-global state. Request blobs are allocated under the caller's memory context. `mdscli_blob_get_path()` increments the parent context id through `mdscli_new_ctx_id()`. Temporary dalloc state is freed before return after packing.

Dependencies and integration points: Depends on mdssvc protocol types, private mdssvc client state, dalloc helpers, and Spotlight marshalling. Called by `cli_mdssvc.c` immediately before `dcerpc_mdssvc_cmd_send()`.

Risks: The request schema is mostly implicit and magic-string driven, so typos or type-name mismatches will produce server-side failures rather than compile errors. Error paths are repetitive and rely on freeing the root dalloc context. Constants such as batch counts, CNID marker `0xadd`, and context `0x6b000020` may be version-sensitive. `talloc_set_name()` is used to make dalloc type lookup work, making memory naming part of wire construction.

Test signals: Blob round-trip tests should unpack each generated blob and assert command selector, context ids, query dictionary keys, scope/query strings, CNID container fields, max-fragment behavior, and no-memory/error propagation from each dalloc insertion point.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_mdssvc_util.c -->
