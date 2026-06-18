# sources/user-network-fs/samba/source3/torture/nbench.c

## Purpose
`nbench.c` implements the newer asynchronous `NBENCH2` replay engine for `smbtorture3`. It reads `client.txt`, parses scripted SMB operations and expected statuses, issues asynchronous client calls, and fails on unexpected NTSTATUS results.

## Important APIs, types, and functions
`struct nbench_state` holds the event loop, `cli_state`, client-name substitution string, input file, open-file table, and optional bandwidth callback. `struct nbench_cmd_struct` stores parsed parameters, expected status, and `enum nbench_cmd`. `nbench_parse`, `nbench_cmd_send`, `nbench_cmd_done`, `status_wrong`, `nbench_send`, `nbench_done`, and `run_nbench2` are the key functions.

## Control flow
`run_nbench2()` opens `client.txt`, creates a tevent context, opens one SMB connection, and polls an `nbench_send` request. The replay loop reads one line, tokenizes it with shell-style splitting, converts the trailing status token, maps the command name, and currently implements async handlers for `NTCreateX`, `Close`, `Mkdir`, and `QUERY_PATH_INFORMATION`. Successful creates add an `ftable` entry; closes remove it. EOF completes the parent request.

## State and persistence behavior
Runtime state includes the open-file linked list and any files/directories created by replayed operations. Script path names replace `client1` with the configured client name. Persistent server-side state depends on the script and is not fully cleaned by this file.

## Dependencies and integration points
It uses Samba async client APIs (`cli_ntcreate_send`, `cli_close_send`, `cli_mkdir_send`, `cli_qpathinfo_send`) and tevent NTSTATUS helpers. It is registered as `NBENCH2` in the torture harness; the older `nbio.c` path supports classic generated replay functions.

## Risks and test signals
Only a subset of parsed commands is implemented; unsupported commands return `NT_STATUS_NOT_IMPLEMENTED`. The expected-status check intentionally converts unexpected success into `NT_STATUS_INVALID_NETWORK_RESPONSE`. Missing `client.txt` or unsupported trace content makes the test fail before exercising server behavior.
