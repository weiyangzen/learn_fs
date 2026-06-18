# sources/user-network-fs/samba/source3/rpc_client/wsp_cli.c

Purpose: Windows Search Protocol client helpers for building WSP request messages, connecting to the `MsFteWds` named pipe over SMB2+, sending raw DCERPC transport calls, and decoding row buffers returned by search queries.

Important APIs/types/functions: `init_connectin_request`, `create_querysearch_request`, `create_setbindings_request`, `create_seekat_getrows_request`, `extract_rowsarray`, `wsp_server_connect`, `wsp_request_response`, and `get_wsp_pipe`. The file relies heavily on generated `ndr_wsp` structures, `wsp_request`/`wsp_response`, AQS parser output `t_select_stmt`/`t_query`, and the local `struct wsp_client_ctx` containing a `dcerpc_binding_handle`.

Control flow: connect initialization builds fixed property sets for catalog, machine, locale, query options, scope, and search root, serializes them into opaque connect blobs, and tags the request as `CPMCONNECT`. Query creation walks the parsed where-tree into WSP restrictions, maps selected columns to property specs, and defines a default sort set. Binding creation computes per-row value/status/length offsets and row width for later `CPMGETROWS`. `wsp_request_response` serializes the selected message body at offset 16, back-patches protocol size fields, computes the WSP checksum for selected messages, inserts the header, performs a raw call, and parses the response.

State/persistence behavior: no durable local state is stored. Runtime state is talloc-owned request/response blobs, row binding layouts, decoded variants, and the persistent server-side WSP cursor referenced by handles returned in responses.

Dependencies/integration: integrates Samba client state, SMB2 pipe wait, DCERPC named-pipe transport, tstream binding handles, generated WSP NDR, WSP property metadata helpers, AQS parsing, and low-level endian/buffer utilities.

Risks/test signals: row-buffer decoding is pointer/offset-sensitive, especially 32-bit versus 64-bit address handling, variable strings, vectors, and length fields. Unsupported fixed-size vectors and arrays return validation errors. Tests should cover connect/create-query/set-bindings/getrows round trips, malformed row buffers, property names including `System.Search.RowID`, checksum/header bytes, and SMB1 rejection in `wsp_server_connect`.
