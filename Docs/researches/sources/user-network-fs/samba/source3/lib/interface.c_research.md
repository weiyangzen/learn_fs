# sources/user-network-fs/samba/source3/lib/interface.c

Purpose: probes, configures, stores, and queries Samba's local network interface list.

Important APIs/types/functions: address/net predicates, interface count/accessors, `load_interfaces()`, `gfree_interfaces()`, `interfaces_changed()`, `interface_ifindex_exists_with_options()`, and internal token parsing helpers.

Control flow: `load_interfaces()` probes kernel interfaces, then either adds broadcast-capable defaults or interprets `interfaces =` tokens by name, wildcard, DNS/IP, IP/mask, broadcast/mask, or synthetic config with optional metadata.

State/persistence behavior: `probed_ifaces`, `total_probed`, and `local_interfaces` are process-global and mirror kernel plus smb.conf state. No durable state.

Dependencies/integration: depends on socket/interface probing, loadparm, sockaddr utilities, FSCTL capability constants, and SMB string parsing.

Risks/test signals: wrong parsing can bind or advertise the wrong interfaces. Tests should cover wildcard/IP/mask/broadcast config, IPv6 link-local scope, dynamic options, change detection, and fallback queries.
