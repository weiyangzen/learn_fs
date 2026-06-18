# File Research: sources/os/bsd/openbsd-src/sbin/iked/print.c

This file prints OpenIKED runtime configuration in iked.conf-like form for verbose/debug output.

Key responsibilities:
- `print_xf` maps transform IDs and key lengths to names from `struct ipsec_xf` tables.
- `print_user` emits a configured user/password line.
- `print_policy` serializes an `iked_policy` including policy mode, active/passive state, IPComp, tunnel/transport, NAT-T, SA protocol, IP protocol filters, address family, rdomain, flow selectors, local/peer constraints, IKE/CHILD SA proposals, IDs, lifetimes, authentication, CP config attributes, interface, pf tag, and tap/enc device.

Important dependencies:
- Relies on transform tables such as `saxfs`, `authxfs`, `ikeencxfs`, `ipsecencxfs`, `prfxfs`, `groupxfs`, `esnxfs`, `methodxfs`, and `cpxfs`.
- Uses `print_verbose`, `print_addr`, `print_proto`, and `print_map` from OpenIKED utility code.
- Uses `if_indextoname` to display configured interface indexes.

Security and correctness notes:
- PSK material is printed when policy auth method is shared-key MIC, so output paths using this function must be treated as sensitive.
- The function walks RB flow trees and TAILQ proposal/config collections and is purely diagnostic; it does not mutate policy state.
