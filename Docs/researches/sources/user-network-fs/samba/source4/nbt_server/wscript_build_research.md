# sources/user-network-fs/samba/source4/nbt_server/wscript_build

## Purpose

`source4/nbt_server/wscript_build` declares the waf build targets for the source4 NetBIOS-over-TCP server, including WINS database support, WINS server/client logic, datagram handlers, the main NBT server subsystem, and the service module.

## Important APIs, Types, and Functions

The script uses `bld.SAMBA_SUBSYSTEM()` and `bld.SAMBA_MODULE()`. Key targets are `WINSDB`, `ldb_wins_ldb`, `NBTD_WINS`, `NBTD_DGRAM`, `NBT_SERVER`, and `service_nbtd`. Autoproto outputs include `wins/winsdb_proto.h`, `wins/winsserver_proto.h`, `dgram/proto.h`, and `nbt_server_proto.h`.

## Control Flow

At build time, WINS DB sources `winsdb.c` and `wins_hook.c` form `WINSDB`; `wins_ldb.c` forms an LDB module; WINS server/client/WACK/DNS proxy sources form `NBTD_WINS`; datagram sources form `NBTD_DGRAM`; interface/register/query/nodestatus/defense/packet/IRPC sources form `NBT_SERVER`; and `nbt_server.c` is registered as `service_nbtd`. All targets are gated by `bld.AD_DC_BUILD_IS_ENABLED()`.

## State and Persistence Behavior

The file persists build graph metadata and generated prototype headers. It does not run runtime state, but its dependency graph determines which WINS/NBT features are linked into AD DC builds.

## Dependencies and Integration Points

Dependencies include `ldb`, `ldbsamba`, `netif`, `samba-hostconfig`, `samba-util`, `cli-nbt`, `WINSDB`, `LIBCLI_DGRAM`, `DSDB_MODULE_HELPERS`, `service`, `LIBNMB`, and `process_model`. The LDB module is external to the `ldb` subsystem while `service_nbtd` integrates with Samba's service framework.

## Risks and Edge Cases

Build gating means non-AD-DC builds may not compile these sources, so changes require AD DC matrix coverage. Autoproto freshness is required because C files include generated headers. Dependency drift can surface as missing symbols in service or LDB-module linkage.

## Test Signals

Signals include a successful AD DC build, generated prototype headers matching source exports, `ldb_wins_ldb` module loadability, and `service_nbtd` starting with `NBTD_WINS` and `NBTD_DGRAM` linked.
