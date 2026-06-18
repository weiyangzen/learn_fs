<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.c -->
# sources/user-network-fs/samba/source3/torture/vfstest.c

## Purpose
`vfstest.c` is the interactive and scripted harness for testing Samba VFS modules without running a full smbd worker. It initializes a synthetic smbd connection rooted at the current directory, registers command sets, parses user commands, and invokes VFS command handlers from `cmd_vfs.c` and optional SMB1 chain tests.

## Important APIs, types, and functions
- `completion_fn()` provides readline command completion from the registered `cmd_list`.
- `next_command()` splits semicolon-delimited `-c` command strings.
- Built-in commands include `cmd_conf`, `cmd_help`, `cmd_debuglevel`, `cmd_freemem`, and `cmd_quit`.
- `add_command_set()`, `do_cmd()`, and `process_cmd()` register command tables, tokenize arguments, dispatch `struct cmd_set` handlers, and report non-OK `NTSTATUS` values.
- `process_file()` executes commands from a script file or stdin.
- `vfstest_get_smbreq()` builds a minimal `struct smb_request` with the synthetic connection and incrementing MID for VFS routines that need request context.
- `main()` handles popt options, Samba command-line/config setup, smbd shim setup, security/locking/file initialization, connection wrapper creation, and command execution.

## Control flow
Startup initializes locale and Samba client/server command-line state, parses `--file`, `--command`, and `--memreport`, sets `umask(0)`, reloads services, installs local smbd exit shims, adds command sets, initializes guest security and locking, creates a `vfs_state`, and calls `create_conn_struct_chdir()` for the current directory. It then executes a command file, a semicolon-separated command string, or an interactive `smb_readline` loop. Every command receives a fresh talloc stackframe, parsed argv array, and the shared `vfs_state`.

## State and persistence behavior
Long-lived state is in `struct vfs_state`: the synthetic `connection_struct`, monotonically increasing SMB message id, up to 1024 open `files_struct` slots, current directory pointer, and command-owned data buffer. `freemem` releases `vfs->data`; `--memreport` reports leaks after each command. Persistent effects are the actual filesystem mutations performed by VFS command handlers under the current working directory and any loaded smb.conf state.

## Dependencies and integration points
The harness integrates with smbd internals (`smbd/smbd.h`, globals, share-mode locks, shim hooks), command-line/config helpers, `SMBREADLINE`, Samba security/session setup, messaging context, `create_conn_struct_chdir()`, POSIX locking, and the external `vfs_commands[]` table. It is built as the `vfstest` binary by `wscript_build`.

## Risks and edge cases
- It runs smbd/VFS internals in a synthetic process; behavior that depends on a real client session, share definition, or daemon lifecycle may not be perfectly represented.
- Command parsing is simple whitespace tokenization and does not provide shell-like quoting semantics beyond `next_token_talloc`.
- `cmd_quit` exits directly from inside command dispatch.
- `process_cmd()` indexes `cmd[strlen(cmd)-1]`, so empty strings should be avoided by callers.
- The process intentionally sets `umask(0)`, so command scripts can create files with broad permissions.

## Test signals
The main signal is whether `vfstest` can initialize and execute command handlers with `NT_STATUS_OK`. Scripted runs via `-f` or `-c` are deterministic entry points for selftests, and `--memreport` exposes command-scoped talloc leaks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/vfstest.c -->
