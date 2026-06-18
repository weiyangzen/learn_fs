# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/dispatch.c

## Purpose
Implements dhclient interface discovery, event loop, timeout scheduling, packet receive dispatch, link-state checks, protocol descriptor management, and unprivileged MTU request sending.

## Main Elements
- `discover_interfaces()`: uses `getifaddrs()` to locate the requested non-loopback, non-point-to-point, up interface; records AF_LINK hardware address/index; registers receive/send descriptors and protocol handler.
- `dispatch()`: infinite `poll()` loop over registered protocols with sorted timeout execution and live-interface checks.
- `got_one()`: receives a packet, handles interface disappearance/error thresholds, and calls `bootp_packet_handler`.
- `interface_status()` / `interface_link_status()`: use `SIOCGIFFLAGS` and `SIOCGIFMEDIA` to decide whether interfaces are active.
- Timeout API: `add_timeout()`, `add_timeout_timespec()`, and `cancel_timeout()` maintain a sorted monotonic timeout list.
- Protocol API: `add_protocol()` and `remove_protocol()` maintain the poll descriptor linked list.
- MTU API: `interface_set_mtu_unpriv()` sends an `IMSG_SET_INTERFACE_MTU`; `interface_set_mtu_priv()` performs privileged `SIOCSIFMTU`.

## Dependencies And Integration
Uses BPF/packet receive functions, `privsep.h` imsg codes, global time variables from `dhclient.c`, and `capsyslog`. The event loop is entered by `main()` after initial state setup.

## Risk Notes
`dispatch()` allocates the poll array once based on initial protocol count while protocols can later be removed; current flow removes dead protocols and uses list traversal, but descriptor count drift is a maintenance concern. Interface disappearance frees interface state after removing its protocol.
