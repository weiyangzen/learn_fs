# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.h

This header defines the `ipsecctl` parser/runtime data model, option bits, enums, transform metadata structures, address wrappers, rule structures, queues, and cross-file function prototypes.

Key contents:
- Command option bit flags for enable/disable/noaction/verbose/show/flush/delete/monitor/showkey/collapse/showflows/showsas.
- Action enum for add/delete.
- Rule type flags:
  - `RULE_FLOW`
  - `RULE_SA`
  - `RULE_IKE`
  - `RULE_BUNDLE`
- Enums for direction, protocol/SA type, tunnel mode, ID type, flow type, auth transforms, encryption transforms, compression transforms, DH groups, IKE active/passive/dynamic mode, IKE auth method, and IKE exchange mode.
- `struct ipsec_addr` union for IPv4/IPv6/address-word views.
- `struct ipsec_addr_wrap` for address, mask, address family, name, linked entries, and source NAT.
- Rule components:
  - hosts, auth, keys, transforms, lifetimes, IKE modes
- `struct ipsec_rule` containing complete parsed rule state: addresses, local/peer, auth, transform/lifetime pointers, keys, tags, generated names, protocols, modes, ports, SPI values, interface, collapsed/bundle queue links, and bundle metadata.
- Queue heads for rule and bundle queues.
- `struct ipsecctl` parser/run state with rule number, options, and queues.
- Prototypes for parser integration, command-line macros, rule management, printing, IKE establishment, and mask setup.

Security and correctness notes:
- This is the shared ABI between parser, main command, IKE generator, and PF_KEY backend.
- The struct owns many heap pointers; cleanup must stay synchronized with parser allocation patterns and `ipsecctl_free_rule`.
