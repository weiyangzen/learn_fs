# sources/user-network-fs/nfs-ganesha/src/support/nfs_read_conf.c

## Purpose
This file defines the table-driven parser metadata for NFS-specific configuration blocks. It maps configuration tokens to fields in global NFS, QoS, Kerberos, directory services, and NFSv4 parameter structures, and supplies small commit helpers for cluster membership.

## Important APIs, Types, And Functions
Exported `config_block` objects include `nfs_core`, optional `qos_core`, optional `krb5_param`, `directory_services_param`, and `version4_param`. Static token lists define UDP listener modes, root Kerberos principal modes, pwnam backends, enabled protocols, RDMA protocol versions, QoS types, NFSv4 minor versions, and recovery backends. Helper functions are `haproxy_host_adder`, `cluster_members_adder`, `remove_self_cluster_members`, and `core_commit`.

## Control Flow
The parser uses `CONF_ITEM_*` macros to populate global config structures with bounds, defaults, token maps, and destination fields. Host-list parameters call custom adders that build client entries. During core commit, local interface addresses are enumerated and any matching `Cluster_Members` entries are moved into `cluster_self`, then cluster members are logged. Most other blocks use `noop_conf_commit`.

## State And Persistence
This file initializes and mutates process configuration state, not persistent files. The parsed values drive server listeners, protocols, DRC sizing, stats, idmapping, QoS defaults, NFSv4 grace/recovery behavior, and security settings for the lifetime of the daemon or until dynamic config reload paths update them.

## Dependencies And Integration Points
It depends on config parsing macros, NFS core structs, FSAL defaults, protocol feature macros, network interface enumeration, export client parsing, pwnam/idmapping headers, and QoS config. The config blocks are consumed by the global Ganesha parser and DBus config interfaces.

## Risks And Test Signals
Risks include very large macro tables where field/default mismatches are easy, feature-guarded options changing the accepted config surface, fatal failure on `getifaddrs` in cluster self-detection, duplicate `glist_del` in `remove_self_cluster_members`, and apparent duplicated text in the QoS IOPS config area. Tests should parse minimal and maximal configs, invalid bounds, all protocol token aliases, cluster member self-removal with IPv4/IPv6 interfaces, QoS-enabled builds, GSS and NFSIDMAP feature variants, and DBus config introspection names.
