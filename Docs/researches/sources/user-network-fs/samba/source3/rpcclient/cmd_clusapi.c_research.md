# sources/user-network-fs/samba/source3/rpcclient/cmd_clusapi.c

## Purpose
`cmd_clusapi.c` adds `rpcclient` commands for Microsoft Cluster API operations. It can query cluster metadata, enumerate cluster objects, open resources/nodes, change resource online/offline state, and pause/resume cluster nodes.

## Important APIs, types, and functions
- Commands use generated `dcerpc_clusapi_*` client stubs from `ndr_clusapi_c.h`.
- Cluster-level query commands cover open/close, name, version, version2, and quorum resource.
- Enumeration commands call `CreateEnum` or `CreateEnumEx`; the latter opens and closes a cluster handle.
- Resource commands open named resources, defaulting to `"Cluster Name"`, then query or change state.
- Node commands open named nodes, defaulting to `"CTDB_NODE_0"`, then pause or resume them.
- `clusapi_commands[]` registers all commands as `RPC_RTYPE_WERROR` against `ndr_table_clusapi`.

## Control flow
Each command parses optional positional arguments, invokes one or more generated RPC stubs using `cli->binding_handle`, translates transport `NTSTATUS` failures to `WERROR`, checks operation-specific `WERROR` results, prints selected returned fields, and closes policy handles where required. Resource and node mutation commands first open a handle, perform the state change, and then close the handle.

## State and persistence behavior
Most commands are read-only, but `clusapi_online_resource`, `clusapi_offline_resource`, `clusapi_pause_node`, and `clusapi_resume_node` mutate remote cluster state. The module maintains no local persistent state beyond command output.

## Dependencies and integration points
This module integrates with `rpcclient` command registration, Samba DCE/RPC binding handles, generated CLUSAPI NDR client stubs, policy handles, and standard Samba error conversion helpers.

## Risks and edge cases
- State-changing commands can disrupt cluster resources or node participation if run against a production cluster.
- Some close calls ignore close failures; this is acceptable for a diagnostic tool but can hide cleanup problems.
- Argument parsing uses `sscanf`/defaults and does not validate extra arguments uniformly.
- `cmd_clusapi_get_resource_state()` checks `Status` after the state call even though the call's final operation result is stored separately.

## Test signals
Test with a controlled CTDB/cluster target: open/close cluster, query names/version/quorum, enumerate with different type masks, open resource, get state, and exercise online/offline or pause/resume only in disposable environments.
