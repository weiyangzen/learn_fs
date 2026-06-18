# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/execute_cmd.c

## Purpose
`execute_cmd.c` parses or accepts command argv arrays and dispatches them to matching request-table functions.

## Important APIs, Types, and Functions
Public functions are `ss_execute_command()` and `ss_execute_line()`. Internal functions are `check_request_table()` and `really_execute_command()`.

## Control Flow
`ss_execute_line()` trims leading whitespace, optionally executes shell escapes prefixed by `!`, parses the line with `ss_parse()`, and dispatches. Dispatch scans each request table and each command alias; on match it records argc/argv/current request in `ss_data`, calls the command function, and clears `current_request`.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes current invocation argc/argv/current_request and shell escape flags. Dependencies are `ss_parse()`, request-table layout, `system()`, and com_err-generated error codes. Risks include shell escape exposure unless disabled, no abbreviation expansion despite fields, and command handlers relying on transient argv memory. Test signals include `test_ss` command execution, unknown-command errors, quoted parsing, and escape-disabled behavior.
