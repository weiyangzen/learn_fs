# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/discover.c

Implements `nvmecontrol discover` for NVMe over Fabrics discovery controllers.

Key behaviors:
- Supports TCP transport and optional HostNQN.
- Connects to the discovery admin queue using shared fabrics helpers.
- Optional `--verbose` prints discovery controller identify data.
- Fetches and prints the discovery log page.
- Decodes transport type, address family, subsystem type, SQ flow-control requirement, secure-channel requirement, port/controller IDs, NQN, transport address/service ID, and RDMA/TCP-specific fields.

Research notes:
- RDMA fields are decoded for display even though active connection support in this group is TCP-only.
