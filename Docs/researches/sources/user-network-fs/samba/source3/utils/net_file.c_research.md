# sources/user-network-fs/samba/source3/utils/net_file.c

Purpose: provides generic `net file` front-end usage and protocol selection for listing, inspecting, and closing open files on a server.

Important APIs/types/functions: `net_file_usage()` prints syntax and common help; `net_file()` handles usage/help and selects `net_rpc_file()` or `net_rap_file()`.

Control flow: no arguments print usage. `HELP` prints usage and succeeds. Other commands call `net_rpc_check(c, 0)`; success dispatches RPC, otherwise RAP fallback.

State and persistence: no local persistence. Delegated close commands can close remote open files.

Dependencies/integration: depends on common help functions, RPC/RAP file command implementations, and `net_context`.

Risks: protocol selection is implicit. This wrapper performs little validation, leaving semantics to backends.

Test signals: no-arg/HELP output; RPC-capable dispatch; RAP fallback; list/user/close/info through both backends.
