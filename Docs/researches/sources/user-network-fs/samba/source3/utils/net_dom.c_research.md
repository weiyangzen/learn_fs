# sources/user-network-fs/samba/source3/utils/net_dom.c

Purpose: implements `net dom` commands for remote machine domain join, unjoin, and rename through NetAPI, with optional remote reboot.

Important APIs/types/functions: `net_dom()` initializes libnetapi and dispatches `join`, `unjoin`, and `renamecomputer`. Handlers call `NetJoinDomain()`, `NetUnjoinDomain()`, and `NetRenameMachineInDomain()`. Reboot uses IPC plus initshutdown/winreg RPC fallback.

Control flow: commands parse `key=value` arguments and a `reboot` token, derive `server_name` from `c->opt_host`, call NetAPI, print libnetapi error strings on failure, and optionally set reboot fields on `net_context` before trying shutdown RPCs.

State and persistence: mutates remote domain membership or computer name; optional reboot changes remote system state. No local state is persisted here.

Dependencies/integration: depends on generated initshutdown/winreg NDR tables, libnetapi, SMB IPC connection helpers, and shared credentials/options in `net_context`.

Risks: passwords may be passed on the command line. Required fields are not fully prevalidated, so errors may surface from NetAPI. Remote reboot is disruptive. `--force` adds rejoin-if-joined behavior.

Test signals: join/unjoin/rename success and error paths; missing fields; force rejoin; reboot with initshutdown success and winreg fallback; host targeting; libnetapi init failure.
