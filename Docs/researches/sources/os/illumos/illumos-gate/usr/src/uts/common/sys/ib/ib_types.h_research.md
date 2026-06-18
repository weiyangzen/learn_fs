# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_types.h

This core IBTA primitive-types header defines GUID/GID/LID/PKey/QKey/service-ID and MTU types and constants.

Core definitions:
- EUI-64 masks/shifts, LID ranges, permissive LID, GUID/subnet-prefix typedefs.
- Unicast and multicast GID structs are wrapped in `ib_gid_t`, with convenience macros for unicast and multicast fields.
- GID prefix constants cover default/subnet-local/site-local and multicast prefix/transient flag/scope values.
- Multicast join states, multicast QPN, and IPoIB multicast GID prefixes are defined.
- LID/path-bits, default/invalid PKeys, GSI QKey, privileged QKey bit, PKey/QKey counter types, SM key, ethertype, QPN/EECN, message length, memory virtual address/length, and service ID types are declared.
- `ib_mtu_t` enumerates unspecified, 256, 512, 1K, 2K, and 4K MTUs.
- `ib_time_t` is a timeout exponent with a 6-bit mask.
- Service ID AGN masks and IP-address-derived service ID masks are defined.

Risk-sensitive invariants:
- These are foundational ABI types used across IBTL, OFED compatibility, nexus, and clients.
- Multicast and service-ID constants encode IBTA/IPoIB conventions and must remain stable.
