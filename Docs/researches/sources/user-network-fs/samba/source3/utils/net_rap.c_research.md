# sources/user-network-fs/samba/source3/utils/net_rap.c

## Purpose
This file implements the legacy `net rap` command family over SMB RAP calls. It lists and mutates files, shares, sessions, servers, domains, print queues, users, groups, group memberships, services, and passwords on RAP-capable servers.

## Important APIs, Types, And Control Flow
`net_rap()` dispatches subcommands through `net_run_function()`. Each command opens an IPC connection with `net_make_ipc_connection()`, calls a `cli_Net*`/`cli_RNet*`/print helper, prints callback-formatted output, and shuts down the `cli_state`. File commands enumerate, close, and show open files. Share commands list, add, and delete shares. Session commands list, show details/connections, and delete sessions. Server/domain commands enumerate servers and browse domains. Print queue commands enumerate queues/jobs and delete jobs. User/group commands list/add/delete users and groups and list/add/delete group members. Password changes call `cli_oem_change_password()`. Validate, admin, and service start/stop are explicit not-implemented stubs.

## State And Persistence
The file itself stores no local state. Remote state can be changed through close/delete/add operations for files, shares, sessions, users, groups, memberships, print jobs, and passwords. Formatting callbacks are stateless.

## Dependencies And Integration Points
It depends on RAP-generated types, svcctl generated definitions, SMB client APIs, clirap wrappers, common net helpers, and SMB connection naming helpers. Usage for some commands delegates to non-RAP command usage functions such as `net_file_usage()`, `net_share_usage()`, `net_user_usage()`, and `net_group_usage()`.

## Risks And Test Signals
RAP is legacy and many servers may not support operations; some commands print "not supported" only for specific return values. Input parsing is thin: numeric IDs use `atoi()`, share add splits on the first `=`, and fixed RAP name buffers truncate through `strlcpy()`. Some allocated comments are not explicitly freed before process exit. Test against a RAP-capable fixture for list/add/delete flows, unsupported server responses, long names/comments, share paths containing `=`, password change errors, and not-implemented command behavior.
