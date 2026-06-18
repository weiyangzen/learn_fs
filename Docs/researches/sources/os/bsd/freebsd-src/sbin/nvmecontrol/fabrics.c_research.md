# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.c

Shared NVMe over Fabrics helper implementation used by connect and discover commands.

Key behaviors:
- Generates default HostNQN and hostid from host UUID.
- Parses address strings in forms including `host:port`, `IPv4:port`, `[IPv6]:port`, bare IPv6, and bare host.
- Parses controller IDs `dynamic`, `static`, or numeric static values.
- Resolves TCP endpoints with `getaddrinfo()`, opens sockets, and connects them for libnvmf qpairs.
- Connects to discovery admin queues, enables controller CC.EN, and waits for CSTS.RDY.
- Connects NVM admin queue, configures controller CC fields, waits ready, identifies controller, requests I/O queues, creates I/O qpairs, and handles cleanup on failures.
- Shuts down controllers by setting CC.SHN before freeing admin qpair.

Research notes:
- TCP is the only implemented transport path here.
- Connection setup preserves reserved controller configuration bits while clearing known fields.
- Error paths use sysexits-compatible return codes for callers.
