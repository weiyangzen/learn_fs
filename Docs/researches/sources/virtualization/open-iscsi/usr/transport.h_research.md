# File Research: sources/virtualization/open-iscsi/usr/transport.h

Purpose: Declares iSCSI transport metadata, behavior hooks, and module-loading/template matching APIs.

Key definitions:
- `enum set_host_ip_opts` describes whether a transport does not support, requires, or optionally uses host IP configuration.
- `struct iscsi_transport_template` names a transport and declares feature flags (`rdma`, `set_host_ip`, `use_boot_info`, `bind_ep_required`, `no_netdev`, `sync_vlan_settings`) plus hooks for endpoint connect/poll/disconnect, connection creation, network config, and ping.
- `struct iscsi_transport` represents a runtime data-path provider with list linkage, kernel handle, capabilities, name, session list, and selected template.

Declared APIs:
- `set_transport_template()`
- `transport_load_kmod()`
- `transport_probe_for_offload()`

Dependencies and interactions:
- Includes project `types.h` and `config.h`.
- Forward-declares `struct iscsi_transport` and `struct iscsi_conn`; hook signatures also refer to `struct iface_rec` and `struct iscsi_session`.

Filesystem/storage relevance:
- Defines the abstraction boundary between iSCSI session management and the actual network/storage transport implementation.
