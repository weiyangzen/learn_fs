# sources/user-network-fs/samba/source3/rpcclient/cmd_srvsvc.c

Purpose: this module implements SRVSVC commands for server metadata, share management, sessions, files, disks, connections, name validation, and file security.

Important APIs, types, and functions: exported handlers call generated `dcerpc_srvsvc_*` functions for `NetSrvGetInfo`, `NetShareEnum`, `NetShareEnumAll`, `NetShareGetInfo`, `NetShareSetInfo`, `NetRemoteTOD`, `NetFileEnum`, `NetNameValidate`, `NetGetFileSecurity`, `NetSessDel`, `NetSessEnum`, `NetDiskEnum`, `NetConnEnum`, `NetShareAdd`, and `NetShareDel`. Display helpers decode server type flags and share info levels 1, 2, 502, and 1005.

Control flow: handlers parse optional info levels and resume handles, initialize the correct level-specific container, call the SRVSVC RPC, convert transport `NTSTATUS` to `WERROR`, then print selected results. Share set operations read existing info, mutate selected fields, write it back, and re-read for display.

State and persistence: most commands are read-only. `netsharesetinfo`, `netsharesetdfsflags`, `netshareadd`, `netsharedel`, and `netsessdel` mutate remote server state. No local persistence is maintained.

Dependencies and integration: depends on SRVSVC NDR, security descriptor display, string wrappers, and `rpcclient` command dispatch. The command table is `srvsvc_commands[]`.

Risks: a few usage checks are permissive enough that missing required arguments can still be dereferenced. Many info levels are accepted but not displayed. Share add/set/delete can disrupt live service if used against production.

Test signals: exercise share enumeration at levels 1, 2, 502, and 1005; validate resume-handle behavior; test add/set/delete on disposable shares; verify file security printing; check invalid info levels and missing arguments.
