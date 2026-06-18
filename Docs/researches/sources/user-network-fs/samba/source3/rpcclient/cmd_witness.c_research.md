# sources/user-network-fs/samba/source3/rpcclient/cmd_witness.c

Purpose: this module provides Witness protocol commands for interface discovery, registration, unregistration, and asynchronous notifications.

Important APIs, types, and functions: handlers call `dcerpc_witness_GetInterfaceList`, `Register`, `RegisterEx`, `UnRegister`, and `AsyncNotify`. It uses `popt` for option parsing, `struct policy_handle` for context handles, `GUID_from_string`, and Witness notify unions. `use_only_one_rpc_pipe_hack` intentionally reuses one pipe for every Witness subcommand.

Control flow: list prints interface flags/state/address/version. Register commands parse version/net/ip/share/client/flags/timeout options and print a `handle_type:guid` token. Unregister and notify parse that token back into a policy handle. Async notify temporarily sets the binding timeout to `UINT32_MAX`, waits for response, then restores the old timeout.

State and persistence: server registration context is stateful and only meaningful on the same RPC connection. The module mutates command-table `rpc_pipe` pointers so all Witness commands share the current pipe.

Dependencies and integration: depends on generated Witness NDR and popt. Registered as `witness_commands[]` and compiled with `RPC_NDR_WITNESS`.

Risks: the pipe reuse hack is global to the command table and can surprise generic rpcclient cache logic. Notify can block indefinitely. The IP address info printer appears to test `WITNESS_IPADDR_ONLINE` for both Online and Offline labels, which may misreport offline state.

Test signals: list interfaces, register V1/V2 and RegisterEx, pass printed handles to notify/unregister in the same session, interrupt long notify waits, and test malformed handle strings.
