# sources/user-network-fs/samba/source3/utils/net_proto.h

## Purpose
This header is the frozen collected prototype surface for the Samba `net` utility. It lets the many command modules call each other and the common net utility layer without relying on generated prototypes.

## Important APIs, Types, And Control Flow
The file declares entrypoints for ADS, DNS update, cache, conf, domain/file/group/groupmap/help/idmap/join/offlinejoin/lookup/RAP/registry/RPC/share/status/time/user/usershare/eventlog/printing/serverid/notify/tdb/vfs/witness commands. It also declares shared helpers such as `run_rpc_command()`, `net_run_function()`, `net_display_usage_from_functable()`, IPC connection helpers, server discovery helpers, SID/name lookup helpers, file copy helpers, printer migration internals, and RPC shell command providers.

## State And Persistence
The header has no runtime state. It shapes cross-module linkage for functions that may read/write remote servers, local TDBs, registry databases, secrets, and Samba configuration through their implementations.

## Dependencies And Integration Points
It includes ADS status and generated libnet join types and references many structs from other subsystems: `net_context`, `cli_state`, `rpc_pipe_client`, `ndr_interface_table`, `dom_sid`, `copy_clistate`, `net_dc_info`, and RPC shell structures. It is included by net command modules as the central declaration contract.

## Risks And Test Signals
Because it is manually frozen, prototypes can drift from implementations if signatures change. It also exposes broad subsystem coupling from a single header, increasing rebuild and include-order sensitivity. Test signals are full `net` utility builds with warnings-as-errors, compile coverage for optional ADS/Kerberos/RPC features, and link coverage for every declared command entrypoint.
