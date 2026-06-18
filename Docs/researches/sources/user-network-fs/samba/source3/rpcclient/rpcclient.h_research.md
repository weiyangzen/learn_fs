# sources/user-network-fs/samba/source3/rpcclient/rpcclient.h

Purpose: this header defines the command handler contract shared by `rpcclient.c` and all command modules.

Important APIs, types, and functions: it includes `rpc_client/cli_pipe.h`, defines `RPC_RETURN_TYPE` with `RPC_RTYPE_NTSTATUS`, `RPC_RTYPE_WERROR`, and `RPC_RTYPE_BINDING`, and defines `struct cmd_set`. The structure holds command name, dispatch function pointers, NDR interface table, cached pipe pointer, help text, usage, and a `use_netlogon_creds` flag. It also exports `rpcclient_msg_ctx` and `rpcclient_netlogon_creds`.

Control flow: no executable control flow exists in the header, but `returntype` determines which function pointer `do_cmd` calls and whether a command needs a bound pipe or can mutate the binding itself.

State and persistence: the `rpc_pipe` field is mutable process-local cache state for each command entry. External globals expose shared messaging and netlogon credential contexts.

Dependencies and integration: every command module includes this file and populates arrays of `struct cmd_set`. `rpcclient.c` consumes those arrays to build its command list.

Risks: the structure has no compile-time guard ensuring the correct function pointer is set for the declared return type; invalid entries are caught at runtime. Shared mutable `rpc_pipe` fields can carry state across commands.

Test signals: build all command modules, run `help`, ensure invalid command entries are rejected, and verify binding-only commands work with `cli == NULL` pipe pointers.
