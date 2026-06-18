# sources/user-network-fs/samba/source4/client/client.c

## Purpose
Implements the Samba4 `smbclient` command-line program. It supports interactive and scripted SMB file operations, share enumeration, NetBIOS message sending, file metadata inspection, LSA name/SID/privilege calls, readline completion, and legacy protocol compatibility options.

## Important APIs, types, and functions
- `struct smbclient_context` stores remote current directory, `smbcli_state`, filename mask, newer-than filter, prompt/recurse/lowercase/translation flags, archive handling, print mode, and I/O buffer size.
- `do_connect()` parses UNC service names, initializes `remote_cur_dir`, stores the global readline context, and calls `smbcli_full_connection()`.
- `commands[]` maps command names, handlers, help strings, and completion hints; `process_tok()` allows unambiguous abbreviations.
- File transfer APIs include `do_get()`, `do_put()`, `cmd_get()`, `cmd_put()`, `cmd_mget()`, `cmd_mput()`, `cmd_reget()`, and `cmd_reput()`.
- Directory and listing logic centers on `do_list()`, `do_list_helper()`, the global NUL-separated `do_list_queue`, `cmd_dir()`, and `cmd_du()`.
- Metadata and administration commands include `cmd_fsinfo()`, `cmd_allinfo()`, `cmd_eainfo()`, `cmd_acl()`, `cmd_lookup()`, and privilege add/delete/list handlers.
- UNIX extension commands include `cmd_link()`, `cmd_symlink()`, `cmd_chmod()`, and `cmd_chown()`, guarded by `CAP_UNIX`.
- Entry points are `main()`, `process_command_string()`, and `process_stdin()`.

## Control flow
`main()` initializes talloc, command-line parsing, Samba config and credentials, SMB options, GENSEC, and tevent. It then follows one of three paths: `-L` share query through `do_host_query()`, `-M` message sending through `do_message_op()`, or normal service connection through `do_connect()`. After connecting it optionally changes the starting remote directory, then runs `-c` semicolon-separated commands or the readline loop.

Interactive command processing tokenizes shell-like arguments with `str_list_make_shell()`, resolves abbreviations through `commands[]`, and invokes command handlers. Recursive remote listing uses a process-global queue rather than call-stack recursion. CNAME-like command aliasing is done by multiple table rows, for example `ls` uses `cmd_dir()` and `rm` uses `cmd_del()`.

## State and persistence behavior
The program persists remote filesystem changes through SMB create, write, unlink, mkdir/rmdir, rename, NT create/open/close, ACL/info queries, UNIX extension calls, and LSA RPC calls. Local persistence includes downloaded files, temporary pager files, local cwd changes via `lcd`, local recursive scans for `mput`, environment-driven password lookup, and shell execution through `!`. In-memory state is mostly in `smbclient_context`, but listing, completion, readline keepalive, transfer totals, and directory totals use file-scope globals.

## Dependencies and integration points
This file integrates Samba's raw SMB client, srvsvc DCERPC share enumeration, LSA helpers, NDR-generated structures, readline wrapper, resolver, GENSEC, loadparm, and credential command-line support. `test_smbclient.sh` blackbox-tests many commands. It also exercises legacy protocol negotiation via `-m LANMAN1` and `-m LANMAN2`.

## Risks and edge cases
- Several helpers use process-global state (`rl_ctx`, listing queue globals, totals), so concurrent or reentrant use is not supported.
- Some talloc usage is legacy by design (`TALLOC_DEPRECATED`, `talloc_append_string(NULL, ...)`) and may leak until process exit.
- `cmd_mget()` appears to build a mask from `remote_cur_dir`, then immediately replaces it with `args[i]`; path handling deserves regression tests.
- `cmd_reput()` builds `local_name` using the remote current directory prefix, which looks suspicious for a local-file operation.
- Shell escape (`!`) intentionally executes local commands from interactive input.
- Error returns are inconsistent: many commands print and return success even when individual SMB operations fail.
- Raw string manipulation of DOS paths, recursion, and local path trimming is fragile around unusual names.

## Test signals
`test_smbclient.sh` covers listing with authentication and anonymous mode, `mput`/`mget`/`put`/`get`, alternate names, `allinfo`, EA info, mkdir/cd/rmdir/rename/deltree, many `fsinfo` levels, SID/name lookup, old protocol listings, `pwd`, and credential sources (`--authentication-file`, `PASSWD_FILE`, `PASSWD`, `USER`). Gaps include readline completion, shell escape, ACL/privilege mutation, UNIX extensions, recursive transfer edge cases, message mode, and many failure paths.
