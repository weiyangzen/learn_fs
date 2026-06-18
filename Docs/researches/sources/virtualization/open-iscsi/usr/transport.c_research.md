# File Research: sources/virtualization/open-iscsi/usr/transport.c

Purpose: Defines built-in iSCSI transport templates, probes/loads kernel transport modules, and attaches runtime transport records to matching templates.

Key entry points:
- `transport_probe_for_offload()` enumerates network interfaces, identifies Ethernet devices, maps netdevs to iSCSI transport names, and attempts to load matching kernel modules.
- `transport_load_kmod()` loads a transport module with libkmod, including special module-name mappings for `tcp` -> `iscsi_tcp` and `iser` -> `ib_iser`.
- `set_transport_template()` matches an `iscsi_transport` name to a static template and stores the template pointer.

Transport templates:
- `iscsi_tcp`: software TCP path using userspace TCP endpoint functions.
- `iscsi_iser`: RDMA/iSER path using kernel transport endpoint functions and `iser_create_conn()`.
- `cxgb3i` and `cxgb4i`: Chelsio offload transports with bind-required endpoint handling and cxgbi connection creation.
- `bnx2i`: Broadcom offload transport requiring host IP setup, boot info, uIP net config, and uIP ping.
- `be2iscsi`: offload transport with VLAN sync and custom connection creation.
- `qla4xxx` and `ocs`: bind-required kernel endpoint transports.
- `qedi`: offload transport requiring host IP, boot info, no netdev, uIP net config, and uIP ping.

Implementation notes:
- `transport_probe_for_offload()` uses `if_nameindex()`, an AF_INET datagram socket, and `SIOCGIFHWADDR` to restrict probing to Ethernet-like interfaces.
- Module insertion uses `kmod_module_probe_insert_module()` with `KMOD_PROBE_APPLY_BLACKLIST`.
- Missing or unknown templates are logged as likely requiring updated userspace tooling.

Dependencies and interactions:
- Uses endpoint functions from TCP I/O, netlink kernel transport (`ktransport_ep_*`), and offload-specific modules (`cxgbi`, `be2iscsi`, `iser`, `uip_mgmt_ipc`).
- Uses network utility `net_get_transport_name_from_netdev()` and error constants from `iscsi_err.h`.

Filesystem/storage relevance:
- Transport selection decides whether iSCSI storage sessions use software TCP, RDMA, or hardware offload paths, and controls how network endpoints and host IP configuration are established.
