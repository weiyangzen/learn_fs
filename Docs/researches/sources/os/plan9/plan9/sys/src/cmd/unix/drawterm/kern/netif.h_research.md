# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/netif.h

Defines shared structures and qid helpers for multiplexed network-style devices.

Contents:
- Qid type constants for clone, address, data, ctl, stat, type, and interface-stat files.
- `NETTYPE`, `NETID`, and `NETQID` macros for packing multiplexed qids.
- `Netfile` state for a per-open network endpoint: owner, permissions, mode, queue, multicast/promiscuous flags, scan settings.
- `Netaddr` for tracked network addresses with hash and allocation chains.
- `Netif` for an interface: file table, address metadata, multicast state, statistics, and hardware callback hooks.
- Ethernet constants and `Etherpkt` layout.

Role:
- Used by `devpipe.c` for qid packing and intended for network interface device implementations.
