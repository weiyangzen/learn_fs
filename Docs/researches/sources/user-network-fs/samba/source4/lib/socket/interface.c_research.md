# sources/user-network-fs/samba/source4/lib/socket/interface.c

## Purpose

`interface.c` builds and queries Samba's configured local network interface list. It interprets `interfaces =` configuration entries, probes kernel interfaces, filters duplicates/loopback, and provides helper queries for IP, broadcast, netmask, best local source IP, local-network membership, same-net checks, and wildcard bind addresses.

## Important APIs, Types, and Functions

`struct interface` stores linked-list pointers, name, flags, sockaddr IP/netmask/broadcast, and string copies. Internal helpers are `iface_list_find()`, `add_interface()`, and `interpret_interface()`. Public helpers include `load_interface_list()`, `iface_list_count()`, `iface_list_n_ip()`, `iface_list_first_v4()`, `iface_list_n_is_v4()`, `iface_list_n_bcast()`, `iface_list_n_netmask()`, `iface_list_best_ip()`, `iface_list_is_local()`, `iface_list_same_net()`, and `iface_list_wildcard()`.

## Control Flow

`load_interface_list()` probes kernel interfaces with `get_interfaces()`. If no config list is set, it adds all non-loopback probed interfaces. If config tokens exist, each token is interpreted as an interface-name pattern, DNS/IP address, IP/masklen, IP/mask, network/mask, or broadcast/mask. Matched probed interfaces are added; otherwise explicit IP/mask tokens can create synthetic interface entries. Query helpers then walk the linked list to return indexed properties or match destination addresses against interface networks.

## State and Persistence Behavior

The interface list is allocated under the supplied talloc context and is otherwise in-memory only. String forms are stored to avoid static-buffer lifetime problems from address formatting. No system network configuration is changed.

## Dependencies and Integration Points

It depends on system networking headers, loadparm `lpcfg_interfaces()`, `lib/socket/netif.h`, util_net address helpers, Samba linked-list macros, and robust string-to-number conversion. Other Samba networking code uses the generated list for binding, source address selection, and local-network decisions.

## Risks and Edge Cases

`interpret_interface()` mutates config token strings when stripping `;` extras and splitting `/`, so it relies on writable configuration storage. IPv4 interfaces without broadcast or loopback flags are skipped. If no usable interface remains, only warnings are logged. Synthetic interfaces trust user-provided masks. Ordering is intentionally preserved with `DLIST_ADD_END()` because some tests depend on it, so changes to insertion order can be visible.

## Test Signals

Tests should cover empty config with loopback filtering, wildcard interface-name matches, DNS/IP tokens, CIDR and explicit netmask tokens, broadcast/network address tokens, duplicates, IPv6 behavior, best-source selection, local-network checks, wildcard list generation, and config entries with semicolon metadata.

Source-read signal: reviewed complete local file (530 lines).
