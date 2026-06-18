# sources/user-network-fs/impacket/examples/mssqlclient.py

## Purpose

`mssqlclient.py` is an interactive or scripted Microsoft SQL Server TDS client. It authenticates to MSSQL with SQL authentication, Windows authentication, hashes, Kerberos, or AES key support, then exposes Impacket's SQL shell for queries and administrative commands.

## Important APIs, Types, and Functions

The script is CLI-only. It constructs `tds.MSSQL(target_ip, port, remoteName, workstation_id, application_name, client_interface_name)`, calls `connect()`, authenticates with `kerberosLogin()` or `login()`, prints server replies, and on success creates `SQLSHELL(ms_sql, show_queries)`. Commands can come from `-file`, `-command`, or the interactive shell.

## Control Flow

After parsing target and options, the script prompts for a password when needed, defaults `target_ip`, forces Kerberos when an AES key is provided, and opens the MSSQL TCP connection. Authentication exceptions are logged and set `res=False`. If authentication succeeds, commands are replayed in order from file or CLI, otherwise `cmdloop()` starts. Finally `disconnect()` is called.

## State and Persistence Behavior

The script does not write local files by itself. It maintains a live TDS connection and an interactive shell object. Remote persistence depends entirely on SQL commands executed by the user or command file. The `-show` flag controls query echoing.

## Dependencies and Integration Points

It depends on Impacket `tds.MSSQL`, `examples.mssqlshell.SQLSHELL`, `parse_target()`, and logger setup. It integrates with SQL Server TDS on port 1433 by default, Windows authentication, Kerberos KDCs, and SQL shell helper commands.

## Risks and Edge Cases

`disconnect()` is called after the shell path, but an exception raised before that point can skip cleanup. `-command` uses `argparse` `extend` with `nargs='*'`, so shell quoting affects command grouping. Password prompting is skipped when AES or hashes are supplied. Query execution can have arbitrary remote database effects. The code does not wrap `ms_sql.connect()` in the authentication try block.

## Test Signals

Tests should mock `tds.MSSQL` and `SQLSHELL` to verify connection parameters, login mode selection, command-file replay, command-list replay, interactive fallback, and disconnect on normal paths. Integration tests should cover SQL auth, Windows auth, Kerberos auth, database selection, custom client properties, failed logins, and SSL/TDS negotiation behavior.
