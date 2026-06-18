# sources/user-network-fs/samba/source4/nbt_server/register.c

## Purpose

`register.c` registers and refreshes the Samba NBT server's NetBIOS names on local broadcast interfaces, the wildcard broadcast interface, and configured WINS servers.

## Important APIs, Types, and Functions

Public functions are `nbtd_register_name()` and `nbtd_register_names()`. Internal pieces include `refresh_completion_handler()`, `name_refresh_handler()`, `nbtd_start_refresh_timer()`, `struct nbtd_register_name_state`, `nbtd_register_name_handler()`, and `nbtd_register_name_iface()`.

## Control Flow

`nbtd_register_names()` registers the server NetBIOS name as client/user/server, aliases as client/server, AD DC workgroup PDC/logon names when appropriate, the workgroup group name, and permanent `__SAMBA__`/`*` names. Per-interface registration creates an `nbtd_iface_name`, uppercases name and optional scope, sets TTL and flags, links it into the interface, and either marks permanent names active, delegates WINS-interface names to the WINS client, or sends a broadcast registration request. Successful broadcast registration marks the name active, records registration time, and starts a refresh timer. Refresh uses registration packets rather than refresh packets so peers defend conflicts.

## State and Persistence Behavior

The file maintains the in-memory `iface->names` list, `NBT_NM_ACTIVE`/`NBT_NM_CONFLICT` flags, TTL, registration timestamps, and refresh timers. It does not persist names to disk; WINS registration side effects are delegated to WINS client code.

## Dependencies and Integration Points

Dependencies include tevent timers, libnbt broadcast registration APIs, WINS client registration, SAMDB PDC detection, loadparm NetBIOS/workgroup/alias/TTL/scope settings, and server role helpers. It is called from NBT task startup after interfaces and SAMDB are ready.

## Risks and Test Signals

Risks include conflicts leaving names inactive, refresh timeout treated as success for broadcast refresh, timer lifetime tied to name objects, role-dependent PDC/logon registration, and permanent wildcard names being immediately active. Tests should cover successful registration, conflict replies, refresh conflict/error/timeout paths, WINS-interface registration, aliases, AD DC PDC and non-PDC roles, scope uppercasing, TTL-derived refresh time, and permanent names.
