# sources/user-network-fs/samba/source3/rpcclient/cmd_shutdown.c

## Purpose
`cmd_shutdown.c` is the placeholder for rpcclient remote shutdown commands. The historical `shutdowninit` and `shutdownabort` handlers remain in the file, but they are disabled behind `#if 0` with a note directing users to `net rpc shutdown` unless the getopt-based code is reworked.

## Important APIs, types, and functions
- Disabled `cmd_shutdown_init()` would parse `-m`, `-t`, `-r`, and `-f` options and call `cli_shutdown_init()` with message, timeout, reboot, and force flags.
- Disabled `cmd_shutdown_abort()` would call `cli_shutdown_abort()`.
- `shutdown_commands[]` currently exports only the `SHUTDOWN` category header and terminating null command because both command entries are inside the disabled block.

## Control flow
In compiled code, rpcclient sees an empty shutdown command group. The disabled init path would reset global `optind`, iterate `getopt()`, fill local flags, and send an init-shutdown request. The disabled abort path would send a shutdown-abort request and log success or failure at debug level 5.

## State and persistence behavior
The active file has no state or remote side effects. If re-enabled, `shutdowninit` would schedule or force a remote shutdown/reboot on the target host, and `shutdownabort` would attempt to cancel one. The disabled option parsing mutates process-global `optind`, which is the reason noted by the surrounding comment.

## Dependencies and integration points
The active file depends only on `includes.h`, `rpcclient.h`, and `struct cmd_set` registration. The disabled code depends on legacy client shutdown helpers rather than generated DCE/RPC stubs, and its command-table entries reference the initshutdown RPC table and remote shutdown pipe.

## Risks and edge cases
- Re-enabling the block without addressing `getopt()` global state could interfere with rpcclient's own command parsing or other commands in the same process.
- The disabled usage string mentions `-h`, but the option string is `m:t:rf` and no `-h` case exists.
- Remote shutdown is high impact and would need explicit authorization checks, clear test isolation, and probably confirmation if exposed interactively.

## Test signals
Current tests should assert that no `shutdowninit` or `shutdownabort` command is registered. If the block is re-enabled, tests need argument parsing coverage, `optind` isolation across repeated calls, scheduled shutdown and abort behavior against a controlled test server, and verification that `net rpc shutdown` remains the preferred supported path.
