# sources/user-network-fs/samba/source3/rpc_client/wsp_cli.h

Purpose: public header for the source3 Windows Search Protocol client helpers implemented in `wsp_cli.c`.

Important APIs/types/functions: declares `enum search_kind`, `get_kind`, request builders for connect/query/bindings/getrows, `extract_rowsarray`, `wsp_server_connect`, `wsp_request_response`, and `get_wsp_pipe`. It forward-declares generated WSP request structures and `struct wsp_client_ctx` so consumers do not need the private client context layout.

Control flow: the header defines the expected call sequence for WSP consumers: connect to the server with `wsp_server_connect`, initialize a `wsp_request`, send it with `wsp_request_response`, create a query, bind selected columns, fetch rows, and decode row data with the same bindings.

State/persistence behavior: it exposes only opaque runtime state. `struct wsp_client_ctx` ownership remains private to the implementation and is talloc-managed by the caller-provided memory context.

Dependencies/integration: includes `libcli/wsp/wsp_aqs.h` for query parser types and depends on Samba core types such as `TALLOC_CTX`, `DATA_BLOB`, `NTSTATUS`, and generated WSP structures from translation units that include this header.

Risks/test signals: API users must pass consistent `wsp_cpmsetbindingsin` data to `extract_rowsarray` and preserve request lifetimes long enough for response parsing. Compile tests should catch generated type drift; integration tests should cover the public sequence against Windows Search or a WSP-compatible server.
