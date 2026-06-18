# sources/user-network-fs/samba/source3/utils/net_share.c

## Purpose
Provides the top-level `net share` usage text and dispatches share operations to transport-specific implementations.

## Important APIs, Types, and Functions
`net_share_usage()` prints syntax for enumerate, add, delete, allowed users, and migration operations plus common method/flag help. `net_share()` handles `HELP`, then chooses `net_rpc_share()` if `net_rpc_check(c, 0)` succeeds, otherwise `net_rap_share()`.

## Control Flow
No share operation is implemented here. The file is a router: explicit help returns usage, otherwise RPC is preferred and RAP is fallback.

## State and Persistence
No direct state changes occur here. Backend commands may mutate remote share definitions, ACLs, and migrated files.

## Dependencies and Integration Points
Depends on `utils/net.h`, common usage helpers, RPC/RAP share backends, and the generic `net` command context.

## Risks
Backend selection can alter semantics and option support. Usage text must stay synchronized with RPC/RAP implementations.

## Test Signals
Check `HELP`, RPC dispatch, RAP fallback, and usage text for migration, ACL, attribute, timestamp, destination, exclude, and verbose options.
