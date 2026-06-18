# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aggr.h

## Purpose

`aggr.h` defines the user/kernel ioctl ABI for illumos link aggregation configuration and reporting.

## Main ABI

Transmit load-balancing policy bits cover L2, L3, and L4 hashing. LACP mode is off/active/passive, and LACP timer is long/short. Port state is standby or attached. The file caps groups at 256 ports and aggregation keys at 999 due to DLPI/VLAN PPA constraints.

`aggr_lacp_state_t` is a byte-sized bitfield union for LACP actor/partner state, with bit ordering handled for host endianness.

## Ioctls

The ABI structures support create, delete, info, add/remove ports, and modify operations. Creation includes link id, key, ports, policy, MAC, LACP mode/timer, fixed-MAC flag, and force flag. Info separates group-level fields from per-port fields including MAC, state, and LACP state.

## Research Notes

This is networking, not filesystem, but it is an exported illumos driver ABI. Layout stability across ILP32/LP64 is explicitly required.
