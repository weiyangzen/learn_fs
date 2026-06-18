# sources/user-network-fs/samba/source3/rpcclient/rpcclient.c

Purpose: this is the `rpcclient` program entry point and dispatcher. It parses command-line options, connects to SMB/RPC transports, registers all command modules, implements built-in commands, opens RPC pipes lazily, and invokes command handlers.

Important APIs, types, and functions: central types are `struct cmd_set`, internal `cmd_list`, `struct dcerpc_binding`, `struct cli_state`, and `struct cli_credentials`. Important functions include `completion_fn`, `next_command`, `binding_get_auth_info`, `cmd_help`, `cmd_listcommands`, auth commands (`sign`, `seal`, `packet`, `none`, `schannel`, `schannelsign`), `cmd_choose_transport`, `rpccli_ncalrpc_connect`, `do_cmd`, `process_cmd`, and `main`.

Control flow: `main` initializes Samba cmdline state, parses a binding or host, normalizes transport, opens an IPC$ SMB connection for NCACN_NP, builds the command-list from all module arrays, then either executes semicolon-separated `-c` commands or enters a readline loop. `process_cmd` tokenizes input with popt, finds a matching `cmd_set`, and calls `do_cmd`. `do_cmd` lazily opens the module pipe using noauth, SPNEGO/NTLM/KRB5, SCHANNEL, or NCALRPC as requested, sets timeout, dispatches by return type, prints errors, and frees per-command memory.

State and persistence: global state includes command list, timeout, messaging context, cached netlogon creds, default netlogon domain, and cached per-command RPC pipes. Auth and transport changes invalidate incompatible cached pipes.

Dependencies and integration: includes every command table by `extern`, relies on Samba cmdline, credentials, messaging, SMB client, DCERPC binding, readline, passdb, and netlogon credential helpers. Built into the `rpcclient` binary by `wscript_build`.

Risks: cached pipes make stateful behavior efficient but sensitive to auth/transport changes. SCHANNEL and `use_netlogon_creds` paths depend on local trust credentials. `completion_fn` has a cleanup bug that frees `matches[count]` inside a loop instead of `matches[i]` on allocation failure. `-c` result only reflects whether each command ended in an NT error, and later commands overwrite earlier result state.

Test signals: parse binding strings and plain hosts, run `-c` multi-command sequences, switch auth and transport mid-session, exercise NCACN_NP and NCALRPC, validate readline completion, check pipe reuse/invalidation, and run commands requiring netlogon credentials.
