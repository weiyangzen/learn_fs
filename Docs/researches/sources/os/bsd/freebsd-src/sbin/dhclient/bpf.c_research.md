# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/bpf.c

## Purpose
Handles DHCP packet input/output through BPF and raw sockets, with privilege-separated send support.

## Main Elements
- `if_register_bpf()`: opens `/dev/bpfN`, attaches it to an interface, and optionally sets VLAN PCP.
- Write BPF filter: restricts outbound BPF writes to expected IPv4 UDP DHCP traffic.
- `if_register_send()`: configures write BPF, locks filter, limits Capsicum rights, and opens raw UDP socket for unicast sends.
- Read BPF filter: accepts IPv4 UDP packets to the local DHCP port, including VLAN VID 0 priority-tagged traffic.
- `if_register_receive()`: configures read BPF immediate mode, allocates read buffer, installs/locks filter, and limits rights/ioctls.
- `send_packet_unpriv()` / `send_packet_priv()`: marshal DHCP packet send requests over imsg-style buffers to privileged code, then send via BPF broadcast or raw socket unicast.
- `receive_packet()`: reads BPF buffers, walks BPF packet headers, validates complete captures, decodes hardware/IP/UDP headers, and returns DHCP payload.

## Dependencies And Integration
Uses `dhcpd.h`, `privsep.h`, BPF ioctls, Capsicum rights, raw sockets, packet assembly/decoding helpers, and dhclient interface state.

## Risk Notes
BPF packet buffering requires careful offset alignment with `BPF_WORDALIGN()`. Send request validation checks message lengths and packet size before privileged transmission.
