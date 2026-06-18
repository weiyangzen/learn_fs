# File Research: sources/os/bsd/freebsd-src/sys/sys/sockio.h

Socket and network-interface ioctl command definitions.

Key responsibilities:
- Defines socket ioctls for high/low watermarks, out-of-band mark, and process-group ownership.
- Defines multicast routing counter ioctls.
- Defines many interface ioctls for addresses, flags, broadcast/destination/netmask, metrics, capabilities, index, MAC label, name, description, aliases, multicast membership, MTU, media, generic driver data, status, link-layer address, physical tunnel addresses, private data, vnet movement, FIB, tunnel FIB, clone creation/destruction, interface groups, RSS, VLAN PCP, down reason, capability nvlists, and MBIM/UMB data.
- Preserves comments for obsolete or historical ioctl slots.

Important patterns:
- The command namespace is split primarily by ioctl group letters `'s'`, `'r'`, and `'i'`.
- Some values preserve old ABI numbering while newer replacement commands use later numbers.
- `SIOCSDRVSPEC` and `SIOCGDRVSPEC` intentionally share a command number with different direction bits.

Research relevance:
- Public network configuration ABI used by sockets and interface management tooling.
