# sources/user-network-fs/samba/source3/utils/net_rpc_shell.c

## Purpose

`net_rpc_shell.c` implements an interactive shell around selected `net rpc` subcommands. It maintains hierarchical command context, opens the needed RPC pipe for each leaf command, provides readline completion for top-level commands in the current context, and exposes `info`, `rights`, `share`, `user`, and `account` command trees.

## Important APIs, Types, and Functions

`rpc_sh_info()` delegates to `rpc_info_internals()` using the current shell context. The global `this_ctx` tracks the active context for prompt and completion. `completion_fn()` completes command names at the beginning of a line. `net_sh_run()` creates a per-command talloc context, opens an unauthenticated RPC pipe with `cli_rpc_pipe_open_noauth()` using the leaf command's NDR table, runs the leaf callback, then frees the pipe and memory. `net_sh_process()` implements command parsing, context descent, `..`, `help`, and `exit` behavior. `sh_cmds` defines the root shell commands. `net_rpc_shell()` creates the IPC connection, discovers the remote domain SID/name, then runs the readline loop.

## Control Flow

`net_rpc_shell()` rejects arguments, initializes libnetapi, creates an IPC connection, builds the root `rpc_sh_ctx`, calls `net_get_remote_domain_sid()`, sets `this_ctx`, and enters a prompt loop. Each line is parsed with `poptParseArgvString()`. `net_sh_process()` first handles empty input, context-up navigation, exit aliases, and help. It then matches the first token against the current context's command table. For subtree commands, it creates a child context with a longer `whoami`, obtains a subtree command table, and either descends interactively or recursively processes the remaining tokens. For leaf commands, it calls `net_sh_run()` and reports non-OK status.

## State and Persistence

Shell state is an in-memory tree of `rpc_sh_ctx` objects holding the active SMB connection, prompt path, current command name, parent pointer, domain SID/name, and command table. Persistent remote state changes are performed only by leaf commands in other files, such as rights, share, user, and account operations. The shell itself only maintains the IPC connection until exit.

## Dependencies and Integration Points

Dependencies include SMB readline, popt argument parsing, libnetapi initialization, SMB client connection helpers, RPC pipe helpers, SAMR/LSA command subtrees, SID formatting, and the command providers `net_rpc_rights_cmds()`, `net_rpc_share_cmds()`, `net_rpc_user_cmds()`, and `net_rpc_acct_cmds()`.

## Risks

`this_ctx` is global mutable state, so the shell is inherently single-session and not reentrant. `net_sh_run()` leaks its `mem_ctx` if `cli_rpc_pipe_open_noauth()` fails because it returns before freeing it. The shell opens RPC pipes with `cli_rpc_pipe_open_noauth()`, relying on the existing IPC session's authentication context; this is intentional but worth validating for security assumptions. `poptParseArgvString()` allocations for `argv` are not explicitly freed in the loop. Returning `false` from parse errors maps to `0`/`false` from a function declared `int`, which is harmless but inconsistent. Completion only covers first-token command names and not nested arguments.

## Test Signals

Tests should cover interactive and one-line subtree dispatch, `help`, `..`, exit aliases, unknown command recovery, command status reporting, prompt updates, domain SID discovery failure, RPC pipe open failure cleanup, and command completion for unique and multiple prefixes.
