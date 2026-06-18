# sources/user-network-fs/samba/source4/nbt_server/wins/wins_hook.c

## Purpose

`wins_hook.c` implements the optional WINS hook script feature. After WINS database add, modify, or delete operations commit, this code builds a shell command describing the record change and runs the configured script asynchronously in a child process.

## Important APIs, Types, and Functions

`wins_hook()` is the public function. `wins_hook_action_string()` maps `WINS_HOOK_ADD`, `WINS_HOOK_MODIFY`, and `WINS_HOOK_DELETE` to the command action words `add`, `refresh`, and `delete`. The hook command includes the script path, action, NetBIOS name, name type, expire time, and each stored address from `rec->addresses`. It calls `winsdb_addr_list_length()` to downgrade a modify with no addresses into delete semantics.

## Control Flow

The function returns immediately when no script is configured. It validates `rec->name->name` so only alphanumeric characters and `._-` are allowed, then allocates a temporary talloc context, formats the command, appends addresses, ignores `SIGCHLD`, forks, and executes `/bin/sh -c <cmd>` in the child. The parent frees the temporary context and does not wait for the child.

## State and Persistence Behavior

No Samba database state is persisted here. The function affects process state by setting `SIGCHLD` to `SIG_IGN`, which is global to the process. Child execution is fire-and-forget, and hook failures are not reported back to the WINS transaction because calls happen after database commit in `winsdb_add()`, `winsdb_modify()`, and `winsdb_delete()`.

## Dependencies and Integration Points

It depends on WINS DB record structures, talloc, libc process APIs, signal handling, and filesystem/system headers. Its integration point is the WINS DB write layer, which passes `h->hook_script` from loadparm `lpcfg_wins_hook()`.

## Risks and Edge Cases

The script path is injected directly into a shell command and is not shell-escaped; configuration must be trusted. The record name is validated, but address strings and script path are not escaped. Setting `SIGCHLD` process-wide can affect unrelated server code. The child does not close inherited file descriptors, noted by a TODO. The parent ignores script exit status, so operational failure is only visible through external script-side logging.

## Test Signals

Tests should cover disabled hooks, add/modify/delete command strings, modify-with-empty-address conversion to delete, invalid names suppressing execution, fork failure behavior, and hook argument handling for multiple addresses. Process-level tests should ensure no zombies and inspect side effects of `SIGCHLD` changes.
