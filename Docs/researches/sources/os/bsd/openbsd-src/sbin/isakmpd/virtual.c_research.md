# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.c

`virtual.c` implements the higher-level `udp` transport method that wraps plain UDP and NAT-T UDP-encap transports. It owns the listener list, per-address virtual transports, default wildcard IPv4/IPv6 transports, interface probing, transport reinitialization, and NAT-T switching.

Startup registers the virtual transport method, binds all eligible interface addresses through `if_map()`, honors `General:Listen-on`, filters by `bind_family`, and optionally binds wildcard default transports so new addresses can trigger rescans. Interface filtering skips non-IP, unusable wildcard/broadcast-ish addresses, down interfaces, tentative/duplicated/detached IPv6 addresses, and addresses outside the current rdomain.

`virtual_clone()` creates peer-specific virtual transports, with main and encap children as needed. `virtual_send_message()` enables NAT-T when message/exchange flags allow it, preserves translated peer ports, and routes output through either main UDP or encapsulated UDP. `virtual_handle_message()` drops old-port traffic after encapsulation is active.

Notable coupling: depends on `udp.c`, `udp_encap.c`, interface enumeration/ioctl state, NAT traversal flags, exchange state, and transport queues.
