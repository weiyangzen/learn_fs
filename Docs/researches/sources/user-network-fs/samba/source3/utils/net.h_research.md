<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.h -->
# sources/user-network-fs/samba/source3/utils/net.h

## Purpose
`net.h` defines shared data structures, constants, transport flags, translation helpers, and includes for Samba's `net` utility and its many subcommand modules.

## Important APIs, types, and functions
- `struct net_context` is the central option/context object passed to all `net` subcommands. It contains parsed CLI options, credentials, messaging, netlogon, loadparm, output flags, witness options, VFS traversal options, and private data.
- `struct net_dc_info` summarizes domain controller properties.
- `NET_TRANSPORT_*` flags classify local, RAP, RPC, and ADS command transports.
- `struct functable` defines command dispatch entries with function pointer, valid transports, description, and usage.
- `rpc_command_fn` is the common RPC command callback signature.
- `copy_clistate`, `rpc_sh_ctx`, and `rpc_sh_cmd` support share-copy and interactive RPC shell state.
- `_()` wraps gettext when available.
- Constants such as `NET_FLAGS_*` and `NET_MODE_SHARE_MIGRATE` are shared option/mode flags.

## Control flow
The header has no runtime control flow. It establishes the shared ABI: `net.c` fills a `net_context`, command tables refer to `struct functable`, and subcommands inspect flags and context fields to choose transport-specific behavior.

## State and persistence behavior
`net_context` is transient per process invocation, but many fields reference contexts that can mutate persistent Samba state, such as credentials, netlogon credential contexts, messaging, and loadparm. The header itself does not persist data.

## Dependencies and integration points
It forward-declares `struct cli_state`, includes generated LSA types, gettext/libintl support, `utils/net_proto.h`, and `utils/net_help_common.h`. It is included by most `source3/utils/net_*.c` modules.

## Risks and edge cases
- `net_context` has grown into a broad option bag; adding fields can increase coupling and accidental option reuse across subcommands.
- Many boolean options are `int`, reflecting popt storage patterns rather than strict typed state.
- Transport flags must be kept consistent with command implementations or help/dispatch can advertise unsupported modes.
- Header changes can trigger broad recompiles and subtle ABI issues across utility modules.

## Test signals
Successful compilation of all `net_*` modules is the primary interface signal. Runtime `net help` output and subcommand dispatch validate `functable` and transport metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/net.h -->
