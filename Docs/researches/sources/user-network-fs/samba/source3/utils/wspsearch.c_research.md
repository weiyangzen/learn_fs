# sources/user-network-fs/samba/source3/utils/wspsearch.c

## Purpose

`sources/user-network-fs/samba/source3/utils/wspsearch.c` implements a command-line Windows Search Protocol client for querying a remote server's WSP service over IPC/RPC. It builds default or custom WSP SQL queries, binds result columns, polls result counts, retrieves rows, and prints result values. The source was read as a complete 847-line file.

## Important APIs, Types, and Functions

Important functions are `main`, `wsp_connect`, `create_query`, `create_bindings`, `create_querystatusex`, `create_getrows`, `print_rowsreturned`, `is_valid_kind`, and `build_default_sql`. It uses WSP request/response structs, `wsp_client_ctx`, `wsp_cpmsetbindingsin`, `t_select_stmt`, `DATA_BLOB`, and DCERPC binding handles.

## Control Flow

`main` parses `--limit`, `--search`, `--kind`, `--query`, Samba connection, and credential options. It parses `//server/share`, builds default SQL with `Scope`, kind, and phrase clauses unless a custom query is supplied, parses SQL with `get_wsp_sql_tree`, ensures a default `System.ItemUrl` column, connects to `IPC$`, creates a WSP client, sends CPMConnectIn, creates a query, sets bindings, asks query status for result count, then loops `CPMGetRows` requests until rows are exhausted or the requested limit is reached.

## State and Persistence Behavior

The tool maintains only runtime RPC/client state: SMB connection, WSP pipe context, cursor, bindings, row buffers, and talloc contexts. It does not persist query state locally; server-side WSP cursor state exists for the connection lifetime.

## Dependencies and Integration Points

It depends on Samba client cmdline/credentials, `cli_full_connection_creds`, SMB transport parsing, WSP utility/client libraries, SQL/AQS parsing, generated NDR WSP types, DCERPC timeout handling, and talloc/tevent contexts. `wscript_build` enables it only when `bld.env.with_wsp` is true.

## Risks and Edge Cases

Argument parsing assumes `//server/share` syntax and mutates the path in place. Default query construction uses string interpolation, so quote/escaping behavior for phrase/location is important. `is_valid_kind` returns `NULL` on allocation failure despite bool return type. Row retrieval uses fixed initial batch size and magic bookmark/offset constants; incorrect 32/64-bit negotiation affects row decoding. Some popt errors are not explicitly checked because the loop body is empty.

## Test Signals

Tests should cover default SQL construction, invalid kind rejection, custom query path, missing share handling, SQL parse failures, mocked WSP request/response sequences, 32-bit and 64-bit row extraction, zero-result handling, limit enforcement, and network/RPC failure diagnostics.
