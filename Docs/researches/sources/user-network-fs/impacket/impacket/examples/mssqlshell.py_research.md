# sources/user-network-fs/impacket/impacket/examples/mssqlshell.py

## Purpose
`mssqlshell.py` implements an interactive SQL Server shell over an Impacket TDS/MSSQL client. It supports arbitrary SQL execution, linked-server traversal, impersonation, xp_cmdshell and SQL Agent execution, local shell commands, file upload/download through SQL Server features, and database/security enumeration.

## Important APIs, Types, and Functions
- `SQLSHELL(cmd.Cmd)` is the main class. It accepts an SQL client object, an optional TCP shell, and a `show_queries` flag.
- Prompt and output helpers: `set_prompt()`, `postcmd()`, `print_replies()`, and `sql_query()`.
- Interactive command methods include `do_exec_as_login`, `do_exec_as_user`, `do_use_link`, `do_shell`, `do_download`, `do_upload`, `do_xp_dirtree`, `do_xp_cmdshell`, `do_sp_start_job`, `do_lcd`, `do_enable_xp_cmdshell`, `do_disable_xp_cmdshell`, `do_enum_links`, `do_enable_rpc`, `do_disable_rpc`, `do_enum_users`, `do_enum_db`, `do_enum_owner`, `do_enum_impersonate`, `do_enum_logins`, `default`, `emptyline`, and `do_exit`.

## Control Flow
Construction binds the shell to normal stdio or a `TcpShell`, stores the SQL client, initializes the linked-server stack `self.at`, and derives a prompt from `system_user`, `current_user`, and `currentDB`. `sql_query()` wraps SQL through nested `EXEC (...) AT linked_server` calls for the current linked-server stack, optionally prints the query, then delegates to `self.sql.sql_query()`. Most `do_*` commands build SQL text, run it, and print replies/rows.

## State and Persistence Behavior
Local state includes the SQL client, prompt state, `show_queries`, current linked-server stack, current local directory, and optional TCP shell. Remote state can be heavily mutated: enabling/disabling `xp_cmdshell`, changing RPC Out on linked servers, creating SQL Agent jobs, executing OS commands, uploading files via base64 chunks and `certutil`, deleting temporary `.b64` files, and changing execution context. Downloads write local files; uploads read local files and create remote files.

## Dependencies and Integration Points
It depends on `cmd`, `os`, `sys`, `hashlib`, `base64`, `shlex`, and an Impacket MSSQL client with `sql_query`, `printReplies`, `printRows`, `rows`, `colMeta`, and `currentDB`. It is launched by `MSSQLAttack` for interactive ntlmrelayx sessions.

## Risks and Edge Cases
- SQL strings are assembled by interpolation with minimal quoting, so shell inputs can break query syntax or execute unintended SQL.
- Many commands catch all exceptions and silently pass, which obscures failures.
- File upload depends on `xp_cmdshell`, Windows `certutil`, echo chunking, permissions, and MD5 output format.
- `do_download` requires bulk admin permission and assumes returned `BulkColumn` data can be hex-decoded from the client representation.
- Linked-server wrapping manually escapes single quotes but can still be fragile for complex commands.

## Test Signals
Fake SQL-client tests should verify query construction for impersonation, linked-server nesting, xp_cmdshell, file upload chunks, and enumeration commands. Integration tests need SQL Server fixtures with and without xp_cmdshell, bulk operations, linked servers, and impersonation permissions.
