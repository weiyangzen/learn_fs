# sources/user-network-fs/samba/source3/utils/net_rpc_sh_acct.c

## Purpose

`net_rpc_sh_acct.c` implements the `account` subtree for `net rpc shell`. It shows and modifies domain account policy settings such as password length/history/age and account lockout thresholds/windows through SAMR RPC.

## Important APIs, Types, and Functions

The central helper is `rpc_sh_acct_do()`, which opens a SAMR connect handle, opens the shell context's domain SID, queries domain information levels 1, 3, and 12, calls a supplied callback, and optionally writes back one modified info level with `samr_SetDomainInfo`. Callback functions include `account_show()`, `account_set_badpw()`, `account_set_lockduration()`, `account_set_resetduration()`, `account_set_minpwage()`, `account_set_maxpwage()`, `account_set_minpwlen()`, and `account_set_pwhistlen()`. Each RPC-facing wrapper passes the appropriate callback to `rpc_sh_acct_do()`. `net_rpc_acct_cmds()` returns the shell command table.

## Control Flow

Shell dispatch in `net_rpc_shell.c` opens the SAMR pipe and invokes one of these command handlers. `rpc_sh_acct_do()` always reads all three domain info levels before invoking the callback, so show and set operations have the same read prelude. A callback validates its argument count, prints usage or current/changed values, mutates one of the provided info structures, and returns `0` for no save, a positive SAMR info level to save, or a negative value for usage/no-save. The helper switches on that returned level and writes only level 1, 3, or 12.

## State and Persistence

Read-only `show` prints account policy state from SAMR. Set commands persist changes in the remote domain policy database: password policy fields are stored in level 1; lockout threshold, duration, and reset window are stored in level 12. Level 3 is read for display of force-logoff behavior but this file does not provide a setter for it.

## Dependencies and Integration Points

Dependencies include SAMR generated client stubs, Samba time conversion helpers, domain SID data from `struct rpc_sh_ctx`, and the interactive shell command model. The file is not a standalone `net rpc` command; it is installed as `account` by `net_rpc_shell.c`.

## Risks

Numeric parsing uses `atoi()` with no validation for non-numeric text, overflow, negative values, or policy range constraints. Time setters use absolute NT time conversion for durations, which deserves careful validation against SAMR's expected signed interval semantics. `rpc_sh_acct_do()` reads all levels even when a setter needs only one, increasing failure surface. Usage callback failures return negative values that the helper treats as "do not save" but still returns the prior SAMR read status, so command-line error reporting can be ambiguous. The display for "Disconnect users when logon hours expire" depends on interpreting zero force-logoff time and should be checked against domain semantics.

## Test Signals

Tests should cover shell usage errors, valid setters for each command, invalid numeric input behavior, no-write behavior for `show`, correct `SetDomainInfo` level selection, permissions failure, and round-trip display after setting lockout and password policy values.
