# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pf_print_state.c

Formats PF state-table entries and address objects for `pfctl` output.

Key responsibilities:
- Prints `pf_addr_wrap` values in rule/state syntax.
- Prints raw IPv4/IPv6 addresses and optional DNS names.
- Prints host/port pairs with optional rdomain, DNS lookup, and service-name lookup.
- Prints TCP sequence windows and sequence-difference information.
- Prints one `struct pfsync_state` in compact or verbose form.
- Converts netmasks into prefix lengths.

Important functions:
- `print_addr()` handles dynamic interface addresses, tables, ranges, address/mask pairs, `no-route`, `urpf-failed`, and route labels.
- `print_addr_str()` prints numeric IPv4/IPv6 addresses with `inet_ntop`.
- `print_name()` performs reverse lookup via `getnameinfo`.
- `print_host()` prints an address plus optional port, including rdomain and service-name formatting.
- `print_seq()` prints TCP state peer sequence low/high/diff fields.
- `print_state()` formats a full PF state, including interface, protocol, translated and original endpoints, routing address, direction arrow, protocol state names, counters, timers, rule/anchor IDs, flags, and state ID.
- `unmask()` calculates the prefix length from a `struct pf_addr` mask.

Notable behavior:
- Dynamic interface output includes modifiers such as `:network`, `:broadcast`, `:peer`, and `:0`, and verbose mode includes dynamic address/table counters.
- A zero address and zero mask prints as `any`.
- Table addresses print as `<name>` or `<name:count>` in verbose mode.
- For inbound versus outbound states, `print_state()` swaps source/destination peers and wire/stack keys to present traffic direction coherently.
- ICMP and ICMPv6 state printing copies relevant key ports because ICMP identifiers/types are represented through port fields.
- NAT or address-family translation is shown by printing translated endpoints with original endpoints in parentheses.
- Verbose TCP output includes sequence windows and window scaling.
- Verbose state output includes age, expiry, packet/byte counters, anchor/rule IDs, sloppy/pflow flags, source-track, and sticky-address markers.
- Extra-verbose output includes state ID and creator ID.
- Packet and byte counters are copied out and decoded as big-endian 64-bit values.

Dependencies:
- Uses PF and pfsync structures from `net/pfvar.h`.
- Uses TCP state names from `netinet/tcp_fsm.h`.
- Uses address formatting helpers and options from `pfctl_parser.h` and `pfctl.h`.
- Uses resolver APIs for protocol, service, and host-name display.

Research notes:
- This is a presentation-only module, but it depends closely on PF state-key semantics, NAT key layout, and byte-order conventions.
