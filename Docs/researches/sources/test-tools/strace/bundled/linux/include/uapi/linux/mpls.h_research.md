# sources/test-tools/strace/bundled/linux/include/uapi/linux/mpls.h

Purpose: declares MPLS label stack entry layout, masks/shifts for RFC label fields, reserved label values, and MPLS link statistics netlink attributes.

Important APIs/types/functions: `struct mpls_label` wraps the big-endian 32-bit label stack entry. Macros extract label, traffic class, bottom-of-stack, and TTL fields. Reserved labels include IPv4/IPv6 explicit null, implicit null, entropy, GAL, OAM alert, and extension labels. `mpls_link_stats` carries per-link counters.

Control flow: route/link tooling and netlink consumers encode/decode MPLS labels, configure routes, and read `AF_MPLS` stats nested under `IFLA_STATS_AF_SPEC`.

State/persistence behavior: the header itself is declarative; MPLS routing and per-link statistics persist in kernel network namespace state and update with packet traffic.

Dependencies/integration: depends on Linux integer types and byteorder definitions. Integrates with rtnetlink, MPLS route configuration, interface stats, and packet parsers.

Risks and test signals: endian handling and bit masking are the core risks. Tests should decode label stack values, reserved labels, bottom-of-stack/TTL/TC fields, and nested MPLS stats attributes.
