# File Research: sources/virtualization/open-iscsi/usr/iface.c

This implementation manages iSCSI iface records: default interfaces, persisted iface config files, matching/binding logic, boot-context conversion, iface printing, iface enumeration, and translation of iface records into kernel netlink parameter buffers.

Major responsibilities:
- Defines built-in default ifaces:
  - `default` using `tcp`.
  - `iser` using `iser`.
- Reads, writes, updates, deletes, and enumerates iface config files under `IFACE_CONFIG_DIR`.
- Protects config file reads/writes with `idbm_lock()` and `idbm_unlock()`.
- Prevents modification/deletion/persistence of special default iface records.
- Creates default offload iface records by scanning SCSI hosts, transport names, hardware addresses, and kernel-exported iface records.
- Copies sparse iface records with `iface_copy()`, only overwriting destination fields that are present/nonzero in the source.
- Validates iface records based on name, transport, and binding by hardware address/netdev/ip/transport.
- Matches iface patterns by iface name and, except for `default`, by transport name.
- Prints iface records in tree or flat forms and links non-default ifaces into lists.
- Builds iface records from boot firmware contexts, including initiator name, MAC, address, VLAN, subnet, gateway, transport, and generated iface name.
- Counts and serializes iface network parameters into `struct iovec` arrays for kernel IPC/netlink setup.

Key control flow:
- `iface_conf_read()` first handles built-in defaults, then reads persisted config under DB lock. If a requested iface is missing, it attempts offload host binding setup once and retries.
- `iface_setup_host_bindings()` creates the iface directory if needed, probes offload transports, scans hosts, and writes generated iface files for offload adapters.
- `iface_for_each_iface()` yields default ifaces unless skipped, then opens `IFACE_CONFIG_DIR`, reads each persisted iface, validates it, and invokes the caller callback.
- `iface_get_param_count()` and `iface_build_net_config()` share filtering by primary hardware address and can operate on one iface or all matching ifaces.
- IPv4 handling supports DHCP or static address/subnet/gateway plus DHCP DNS/SLP/vendor/client-id controls, TOS, ARP, fragmentation, forwarding, TTL, and common TCP/iSCSI parameters.
- IPv6 handling supports address autoconfig, link-local autoconfig, router autoconfig, explicit IPv6/link-local/router addresses, neighbor discovery controls, MLD, flow label, traffic class, hop limit, and common TCP/iSCSI parameters.
- Common parameter serialization covers iface enable, VLAN enable/tag, MTU, port, delayed ACK, Nagle, window scaling, TCP timestamps, redirect, task management timeout, digests, immediate data, initial R2T, ordering, ERL, burst lengths, R2T count, and CHAP/discovery flags.

Important dependencies:
- Uses IDBM metadata/parsing/printing functions from `idbm.h`.
- Uses sysfs and host helpers for offload discovery.
- Uses net helpers for transport lookup and netdev activation.
- Uses `iscsi_netlink.h` allocation/alignment helpers and kernel `iscsi_if.h` net parameter IDs.
- Uses `libopeniscsiusr` accessor APIs for printing `struct iscsi_iface`.

Filesystem/storage relevance:
- This file is the binding layer between configured iSCSI targets and network interfaces. Correct iface binding determines which NIC/offload path carries storage traffic and how firmware/uIP/kernel networking is configured before login.

Notable implementation constraints and risks:
- Several string copies use fixed-size buffers and assume source data already fits the target struct fields.
- `iface_get_iptype()` uses heuristics rather than full address validation.
- IP-address binding is recognized but software TCP binding by IP is explicitly unsupported.
- Parameter counting must stay exactly in sync with parameter construction; otherwise callers may allocate the wrong iovec capacity.
- The code treats zero numeric values as absent for many fields, which can make it impossible to represent a meaningful explicit zero for some parameters.
