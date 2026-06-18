# sources/user-network-fs/nfs-ganesha/src/include/nfs_qosmgr.h

## Purpose

`nfs_qosmgr.h` declares optional DBus management hooks for QoS when `ENABLE_QOS` is compiled.

## Important APIs, Types, and Functions

It exports `g_qos_config_lock`, `dbus_qosmgr_init`, `get_export_client_count`, and `lookup_client(DBusMessageIter *args, char **errormsg)`.

## Control Flow

DBus initialization registers QoS manager methods. DBus handlers lock QoS config, parse client arguments, find client objects, inspect export/client counts, and return errors through `errormsg` when lookup fails.

## State and Persistence Behavior

The header exposes shared QoS config lock and reads live QoS/export/client state. Changes are runtime-only unless implementation writes back to config elsewhere.

## Dependencies and Integration Points

It depends on `gsh_dbus.h`, QoS class definitions from `nfs_qos.h`, client manager types, and DBus message iterators. It integrates with admin/DBus thread initialization and QoS runtime classes.

## Risks and Test Signals

Risks include DBus/QoS lock ordering, stale client pointers, malformed DBus argument handling, and exposing inconsistent counts during reload. Tests should initialize DBus QoS manager, lookup valid/invalid clients, query export-client counts under concurrent client changes, and run with QoS disabled to ensure guarded declarations are not referenced.
