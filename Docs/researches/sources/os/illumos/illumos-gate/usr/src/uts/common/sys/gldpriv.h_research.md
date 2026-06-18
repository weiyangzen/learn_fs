# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gldpriv.h

## Role

`gldpriv.h` defines GLD framework-private STREAMS, DLPI, VLAN, media interpreter, kstat, multicast, source-routing, and lock internals. It backs the driver-facing `gld.h` API.

## Key Interfaces and Data

- Includes a broad networking and STREAMS dependency set: DLPI, DLS, Ethernet, VLAN, IP checksum, kstat, locks, queues, and GLD public definitions.
- Defines GLD version constants and flags for MAC registration/interrupt/lock/unregistration state.
- Defines `GLD_MAX_ADDRLEN` and default multicast table size.
- `gld_mcast_t` tracks per-MAC multicast references and addresses.
- Per-stream flags cover raw mode, fast path, physical/SAP/multicast promiscuity, and close-in-progress.
- `gld_t` is per-stream state: DLPI state/style/minor/type/SAP, flags, multicast table, queue pointer, attached MAC, major device, scheduling flags, VLAN state, user priority, and send routine.
- `glddev_t` is per-major state: MAC list, stream list, device name, lock, clone minor allocation, media attributes, broadcast address, and provider styles.
- `pktinfo_t` describes interpreted packet properties, VLAN fields, lengths, source/destination addresses, ethertype, and acceptance state.
- `packet_flag_t` distinguishes quick receive, looped receive, receive, and transmit interpreter contexts.
- `gld_interface_t` binds media type, MTU, header size, interpreter, fastpath builder, unitdata builder, init/uninit, and media string.
- `media_kstats_t` and `struct gldkstats` mirror public statistics as kstat named values.
- `gld_vlan_t` and `gld_mac_pvt_t` track VLAN hash entries, per-MAC private data, kstats, multicast table, source-routing state, notification support, and start state.
- Lock macros implement GLDM lock lifecycle and rw enter/exit/try/held checks.
- MAC helper macros compare/copy addresses, with canonical-bit-reversal support.
- Alignment-safe macros read/write host/network-order 16-bit fields from possibly unaligned packet data.
- Route Determination Entity and source-routing structures define RDE PDUs, route information fields, route designators, and source-route table entries.
- Defines shared LLC/SNAP, FDDI, token-ring, and DLSAP structures.
- Declares media interpreter, fastpath, VLAN insertion, unitdata, init, and uninit functions for Ethernet, FDDI, token ring, and InfiniBand.

## Dependencies and Use

This is GLD implementation-private and should not be used by device drivers directly. It is tightly coupled to `gld.c` and media helpers such as `gldutil.c`.

## Research Notes

The file shows GLD as a legacy DLPI/STREAMS compatibility framework with VLAN and multiple media support grafted onto old fixed-layout structures. Lock macros preserve the historic interface while using rwlocks for scalable v2 behavior.
