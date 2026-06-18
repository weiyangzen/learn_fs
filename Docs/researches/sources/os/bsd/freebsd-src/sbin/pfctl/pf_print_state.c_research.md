# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pf_print_state.c

## Purpose
Formats PF runtime state entries for `pfctl` output. It converts kernel/userland state structures into readable addresses, ports, protocol state names, counters, flags, routing metadata, and the rule that created the state.

## Main Elements
- `print_addr()` prints PF address wrappers, including dynamic interface addresses, tables, ranges, masks, `any`, `no-route`, and `urpf-failed`.
- `print_state()` prints one `struct pfctl_state`, including direction-sensitive endpoints, NAT/address-family translation display, protocol state names, age/expiry, packet/byte counters, rule/anchor IDs, flags, routing target, rtable, original interface, and verbose creator rule.
- `unmask()` computes prefix length from a PF mask.

## Dependencies And Integration
Includes PF, TCP, SCTP, networking, resolver, and parser headers. Uses helpers such as `pfctl_proto2name()`, `print_rule()`, PF address macros, state flag constants, and PF state-name arrays.

## Risk Notes
Output depends on exact PF state structure layout and flag definitions. Direction and address-family translation logic is easy to regress because it rewrites which key index is displayed as source or destination.
