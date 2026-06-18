# sources/user-network-fs/samba/source3/rpcclient/cmd_wkssvc.c

Purpose: this module exposes WKSSVC workstation commands for workstation info, join info, message sending, computer-name enumeration, and logged-on user enumeration.

Important APIs, types, and functions: handlers call generated `dcerpc_wkssvc_NetWkstaGetInfo`, `NetrGetJoinInformation`, `NetrMessageBufferSend`, `NetrEnumerateComputerNames`, and `NetWkstaEnumUsers`. It converts outbound message strings with `push_ucs2_talloc`.

Control flow: command handlers use `cli->desthost` as server name, parse optional levels/name type/message, call the RPC, and print selected returned fields. User enumeration prints level 0 names or level 1 domain-qualified names.

State and persistence: queries are read-only except `wkssvc_messagebuffersend`, which sends a remote message. No local persistence.

Dependencies and integration: depends on WKSSVC NDR and `rpcclient.h`, registered by `wkssvc_commands[]`.

Risks: several commands accept optional numeric arguments via `atoi`. `wkssvc_wkstagetinfo` does not print returned workstation info, so success is mostly visible through status. Computer-name enumeration appears to print `ctr->computer_name->string` in each loop instead of indexing a per-entry array.

Test signals: test info levels, join info output, message conversion, name type enumeration, user levels 0 and 1, and invalid/unsupported level returns.
