# sources/user-network-fs/nfs-ganesha/src/include/server_stats_private.h

## Purpose
This private statistics header defines internal aggregate structures, DBus reply signatures, reset/export helpers, and initialization/free APIs for Ganesha server statistics.

## Important APIs, Types, And Control Flow
It forward-declares per-protocol stats types, defines `struct gsh_stats`, `struct gsh_clnt_allops_stats`, `struct server_stats` with trailing variable-sized `gsh_client`, `struct export_stats`, and `struct auth_stats`. Under `USE_DBUS` it defines many DBus type/signature macros for exports, clients, IO, layout, auth, all-ops, LRU, and FD usage, declares DBus serialization functions, reset functions, stats timestamps, and optional protocol-specific emitters. It always declares `server_stats_free`, `server_stats_allops_free`, and `server_stats_init`.

## State And Persistence
It manages process runtime statistics and timestamps such as auth/v3/v4 full stats times. DBus functions serialize current in-memory counters; reset functions clear them. No file persistence is performed.

## Dependencies And Integration Points
It includes `sal_data.h` for client/export/state relationships. It integrates with client manager allocation sizing, export manager stats, DBus introspection/serialization, NFS protocol counters, FSAL operation stats, MDCACHE utilization, and FD usage summaries.

## Risks And Test Signals
The trailing `gsh_client` layout requirement in `server_stats` is memory-layout sensitive. DBus signature macros must match serialization code exactly, and compile-time protocol flags change container shape. Tests should cover DBus introspection/signature validation, stats reset, allocation sizing for variable-length clients, disabled/enabled protocol builds, and monotonic counter behavior under concurrent requests.
