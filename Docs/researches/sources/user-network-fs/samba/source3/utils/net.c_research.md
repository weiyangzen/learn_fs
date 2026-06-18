<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.c -->
# sources/user-network-fs/samba/source3/utils/net.c

## Purpose
`net.c` is the top-level entry point and command dispatcher for Samba's `net` utility. It parses global options and credentials, initializes Samba client context, defines the root command table, and implements several local trust/SID/auth-user commands directly.

## Important APIs, types, and functions
- `get_sec_channel_type()` maps textual secure-channel parameters to `netr_SchannelType`.
- Trust/password helpers include `net_changetrustpw()`, `net_primarytrust_dumpinfo()`, `net_primarytrust()`, and `net_changesecretpw()`.
- Auth-user helpers include `net_setauthuser()` and `net_getauthuser()` for winbind IPC credentials in secrets.
- SID/RID helpers include `net_getlocalsid()`, `net_setlocalsid()`, `net_setdomainsid()`, `net_getdomainsid()`, `search_maxrid()`, `get_maxrid()`, and `net_maxrid()`.
- `net_func[]` is the root `struct functable` dispatch table for `rpc`, `rap`, `ads`, `file`, `share`, `session`, `user`, `group`, `idmap`, `status`, `registry`, `eventlog`, `vfs`, `witness`, and many other subcommands.
- `main()` parses global popt options into `struct net_context`, sets credentials and Kerberos ccache, initializes messaging, and calls `net_run_function()`.

## Control flow
Startup blocks SIGPIPE, initializes locale/gettext, initializes Samba command-line context with client config, sets default log level 0, creates a popt context with many global options, and records parsed values in `net_context`. It derives explicit-credential state from the credentials object, chooses the workgroup/domain, handles legacy NTLM ccache features, determines the Kerberos credential cache name, initializes command-line messaging, applies requester netbios name and default target workgroup, loads network interfaces, initializes security, burns command-line secrets, then dispatches the remaining argv through `net_run_function()`.

## State and persistence behavior
Most persistent state changes are delegated to subcommands. Direct functions here can mutate `secrets.tdb` machine trust data, auth-user credentials, local/domain SIDs, keytab synchronization state, and passdb-derived RID state. `net_context` is request-scoped talloc state carrying all global options and shared contexts.

## Dependencies and integration points
The file integrates with nearly every Samba source3 management subsystem: credentials, gensec, Kerberos, loadparm, messaging, secrets, passdb, libnetapi, ADS/RPC/RAP modules, registry/eventlog/vfs/witness helpers, gettext, and generated `net_proto.h`. Subcommand implementations live across many sibling `net_*.c` files.

## Risks and edge cases
- Many global options are meaningful only to specific subcommands; invalid combinations are often handled downstream.
- `changesecretpw` is intentionally dangerous and requires `-f`, but it directly changes domain member machine account secrets.
- Kerberos ccache selection has several fallback layers and exits if no cache name can be established.
- `get_sec_channel_type("PDC")` maps to `SEC_CHAN_BDC`, preserving historical semantics that can surprise readers.
- Root command dispatch relies on generated prototypes and a large command table, so build coverage across optional features is important.

## Test signals
Command-level tests should cover `net help`, global option parsing, credential handling, `getlocalsid`/`setlocalsid`, `getdomainsid`, `setauthuser`/`getauthuser`, `maxrid`, and representative dispatch into RPC/RAP/ADS/local subcommands. Dangerous secret-changing commands should be tested only in isolated fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.c -->
