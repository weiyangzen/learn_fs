# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/mssqlattack.py

## Purpose
`mssqlattack.py` connects ntlmrelayx MSSQL relay sessions to either an interactive `SQLSHELL` or a configured list of SQL queries.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "MSSQLAttack"` advertises the plugin.
- `MSSQLAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["MSSQL"]`.
- `__init__()` creates a `TcpShell` when `config.interactive` is true.
- `run()` launches `SQLSHELL` in interactive mode, executes configured queries, or logs an error if no queries are configured.

## Control Flow
Interactive mode starts a local TCP shell, listens, wraps the relayed MSSQL client in `SQLSHELL`, and enters `cmdloop()`. Non-interactive mode iterates `config.queries`, logs each query, calls `client.sql_query()`, and prints replies and rows.

## State and Persistence Behavior
Local state is limited to the optional TCP shell. Remote SQL state depends entirely on provided queries or interactive shell actions. The module itself does not write files.

## Dependencies and Integration Points
It depends on `impacket.LOG`, `SQLSHELL`, `ProtocolAttack`, and `TcpShell`. It is registered by the attack loader for MSSQL relay targets.

## Risks and Edge Cases
Interactive mode exposes a local listener on loopback that remains active for the shell lifetime. Non-interactive queries are arbitrary and may mutate SQL Server state. No query timeout or transaction isolation is implemented here.

## Test Signals
Tests should assert interactive shell startup with a fake `TcpShell`, query iteration and output calls, and the no-query error path.
