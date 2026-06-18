# File Research: sources/virtualization/open-iscsi/usr/iscsiadm.c

## Purpose
`iscsiadm.c` implements the `iscsiadm` command-line administration utility. It parses user options into modes, operations, submodes, records, interface filters, and parameters, then coordinates IDBM database operations, discovery, login/logout, session listing, host/iface management, CHAP tables, flashnodes, offload host statistics, pings, rescans, and daemon control.

## Modes and Dispatch
The file defines `enum iscsiadm_mode` for discovery, discoverydb, node, session, host, iface, firmware, ping, CHAP, flashnode, and host stats. It defines bitmask operations for new/delete/update/show/nonpersistent/apply/applyall/login/logout. `main()` parses `getopt_long()` options, validates option legality per mode via `verify_mode_params()`, initializes logging, libopeniscsiusr context, sysfs, IDBM, resource limits, and then dispatches to mode-specific executor functions.

## Discovery and Node Management
- Discovery paths parse SendTargets, iSNS when built, and firmware discovery types.
- `do_target_discovery()` separates offload-capable interfaces from software discovery, can invoke offloaded SendTargets for hardware that supports it, and falls back to software discovery via `idbm_bind_ifaces_to_nodes()`.
- `exec_disc_op_on_recs()` synchronizes discovered nodes with the database: delete stale records, add/update new records, print results, and optionally log in to discovered portals.
- Node mode supports static record creation, record printing through libopeniscsiusr, parameter updates, deletes guarded against active sessions, per-node login/logout, rescans, stats, and login/logout-all by startup policy.
- Leading-login handling separates records with `leading_login` enabled, logs regular portals first, then attempts leading logins per iface while avoiding duplicate sessions for the same target.

## Session and Daemon Operations
- Session mode can operate on a specific sid or all sessions. A specific sid is resolved through sysfs, converted into a node record, and then passed down to node-mode operations.
- `kill_iscsid()` sends `MGMT_IPC_IMMEDIATE_STOP` through the daemon IPC channel.
- `session_stats()` requests `MGMT_IPC_SESSION_STATS` and prints standard iSCSI SNMP-style counters plus transport-provided custom counters.
- `rescan_portal()` scans existing devices for size changes and scans the host for new devices.

## Host, CHAP, Flashnode, and Stats Operations
- Host CHAP operations read, create/update, and delete hardware CHAP entries through transport netlink IPC calls. Parameter verification requires one matching username/password pair and rejects ambiguous pairs.
- Flashnode operations read/list sysfs flashnodes and use netlink IPC to create, delete, update, login, logout, or logout by session ID. The code maps kernel errors such as `-EPERM` and `-ESRCH` into open-iscsi errors.
- Host stats mode requests `iscsi_offload_host_stats` and prints MAC, IP, IPv6, TCP, ECC, and iSCSI counters.
- Host number parsing accepts either a numeric host number or a MAC address, probing offload transports before MAC-to-host lookup.

## Interface and Ping Operations
- Iface mode can create, delete, update, apply one iface, apply all ifaces on a host, list flat configs, or print an iface-to-node tree through libopeniscsiusr.
- Interface updates reject changes that would mutate immutable iface names or switch binding type from MAC to netdev or vice versa. VLAN settings may be synchronized across related offload ifaces when the transport template requests it.
- Ping submode reads iface config, resolves the destination address, applies transport net configuration when needed, and executes either a transport-specific ping hook or IPC ping call. It prints per-packet status text.

## Dependencies and Integration
This file is a hub for nearly every user-space subsystem: libopeniscsiusr, IDBM, discovery, firmware contexts, iface management, sysfs, transport templates, management IPC, netlink IPC, session management, flashnode helpers, timers, logging, and error mapping.

## Risk Notes
- The command dispatcher is large and stateful; many option combinations are rejected only after parsing all options.
- Some operations combine database mutation with live session actions, so active-session checks and safe logout configuration are important guardrails.
- Several executor functions allocate temporary iovec arrays for netlink messages and rely on companion builders to populate matching counts; incorrect parameter counts would affect kernel IPC calls.
- Return conventions differ across callback families (`0` success/match, `-1` no-match, positive error), so new callbacks must match their iterator.
