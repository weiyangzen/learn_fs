# sources/test-tools/stress-ng/core-net.c

Purpose: common network helpers for domain parsing, socket address construction, interface lookup, port reservation, checksum calculation, and port wraparound.

Important APIs/functions: `stress_net_interface_exists`, `stress_net_port_set`, `stress_net_domain`, `stress_net_domain_set`, `stress_net_sockaddr_if_set`, `stress_net_sockaddr_set`, `stress_net_sockaddr_port_set`, `stress_net_reserve_ports`, `stress_net_release_ports`, `stress_net_ipv4_checksum`, and `stress_net_port_wraparound`.

Control flow: domain helpers map `ipv4`, `ipv6`, and `unix` to address families. Socket setup uses static address structs and optional `getifaddrs` interface lookup, otherwise any/loopback addresses. Port reservation builds a Linux busy-port bitmap from `/proc/net/*`, then locks `g_shared->net_port_map` while scanning for a free single port or contiguous range.

State/persistence: uses shared `g_shared->net_port_map.allocated` protected by a lock. Static sockaddr storage is overwritten by each call. Unix socket paths live under `/tmp`.

Dependencies/integration: `core-net.h`, `core-lock.h`, bit macros, parse-option helpers, sockets, `getifaddrs`, procfs, and stressor shared memory.

Risks: static sockaddr buffers are not reentrant; port reservation can race external processes; `/proc/net` parsing is best-effort; release does not take the allocation lock; AF_UNIX path assumes `/tmp`.

Test signals: IPv4/IPv6/Unix address generation, interface binding, invalid domains, busy/contiguous port reservations, concurrent stressors, checksum vectors, and port wraparound.
