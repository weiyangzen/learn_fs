# sources/user-network-fs/samba/source3/rpcclient/cmd_dfs.c

## Purpose
`cmd_dfs.c` provides `rpcclient` commands for the DFS/NETDFS RPC interface. It checks DFS support, adds and removes DFS links, enumerates DFS namespaces, and fetches DFS entry information.

## Important APIs, types, and functions
- `cmd_dfs_version()` calls `dcerpc_dfs_GetManagerVersion()`.
- `cmd_dfs_add()` and `cmd_dfs_remove()` wrap `dcerpc_dfs_Add()` and `dcerpc_dfs_Remove()`.
- Display helpers print supported DFS info levels 1, 2, and 3.
- `cmd_dfs_enum()` and `cmd_dfs_enumex()` prepare the correct `dfs_EnumArray*` union arm for levels 1, 2, 3, 4, 200, or 300 and call `Enum` or `EnumEx`.
- `cmd_dfs_getinfo()` calls `dcerpc_dfs_GetInfo()` and displays levels 1 to 3.
- `dfs_commands[]` registers the commands against `ndr_table_netdfs`.

## Control flow
Commands validate argument count, parse optional info levels with `atoi`, initialize the matching DFS union arm with `ZERO_STRUCT`, call the generated RPC stub, convert transport errors, and print returned entries only on successful `WERROR` results. Add/remove pass caller-provided path, server, share, and comment values directly to the server.

## State and persistence behavior
Version, enum, enumex, and getinfo are read-only. `dfsadd` and `dfsremove` mutate the remote DFS namespace or referral configuration. There is no local persistence.

## Dependencies and integration points
The file depends on `rpcclient.h`, generated NETDFS client stubs, DFS NDR union types, and Samba NTSTATUS/WERROR conversion. It complements the server-side `RPC_NETDFS` subsystem declared in `source3/rpc_server/wscript_build`.

## Risks and edge cases
- Info levels 4, 200, and 300 can be requested for enumeration but display support only handles levels 1 to 3.
- `display_dfs_enumstruct()` assumes count is the first field and reads through `info1`, which depends on compatible generated layout.
- State-changing add/remove commands perform no local validation of DFS path shape.
- `atoi` parsing silently maps invalid level strings to 0.

## Test signals
Use `dfsversion`, `dfsenum`, `dfsenumex`, and `dfsgetinfo` against a test DFS server at levels 1, 2, and 3. Mutation tests should add a disposable DFS link, verify it appears, then remove it.
