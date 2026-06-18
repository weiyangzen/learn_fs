# sources/user-network-fs/nfs-ganesha/src/support/nfs_qosmgr.c

## Purpose
This file exposes runtime QoS management over DBus. It lets administrators inspect and update bandwidth, token, and IOPS limits for per-client, per-export, and per-export-per-client QoS modes.

## Important APIs, Types, And Functions
The only non-static exported function is `dbus_qosmgr_init`. Internally, DBus handlers include client setters/getters for bandwidth, tokens, and IOPS; export setters/getters for bandwidth, tokens, and IOPS; per-export-per-client list/set functions; and enable/disable functions for bandwidth and IOPS control. Static `gsh_dbus_method` arrays `qos_methods_pc`, `qos_methods_ps`, and `qos_methods_pepc` define the method surfaces, and `qos_interface` is registered under `org.ganesha.nfsd.qos`.

## Control Flow
Each DBus handler validates argument types, resolves a client or export, takes `g_qos_config_lock`, optionally takes a target `qos_class->lock`, reads or mutates bucket limits/enable flags, writes DBus reply fields, releases references and locks, and returns a boolean DBus status. `dbus_qosmgr_init` selects the method array based on `g_qos_config->qos_type` and registers path `QosMgr` if QoS is globally enabled.

## State And Persistence
The file mutates live `gsh_client`, `gsh_export`, `qos_block`, and `qos_class_t` structures in memory. Changes are runtime state, not persisted back to configuration files. Locks coordinate concurrent DBus calls and NFS request QoS use.

## Dependencies And Integration Points
It depends on DBus support, export/client lookup helpers, global QoS config from `nfs_qos.h`, Ganesha lock conventions, glist iteration, and `gsh_dbus_register_path`. It is the management-plane companion to request-path QoS enforcement.

## Risks And Test Signals
Risks include several apparent iterator/reply mistakes: some getters append output to `args` instead of the reply iterator, `dbus_qos_client_bw_get` duplicates `lookup_client`, some export getters use `iter` before `dbus_message_iter_init_append`, and some setters validate the same current argument twice without advancing. IP rendering in `client_qos_to_dbus` casts `qos_class->gsh_client` rather than the `cl_addrbuf` field after checking its family, which looks unsafe. Tests should use DBus introspection and method calls for every QoS mode, invalid argument type/order checks, missing export/client checks, concurrent set/get calls, and sanitizer coverage for list rendering.
