# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstatefields.c

Tabular state-entry field definitions and printer.

Key behavior:
- Defines `statefields[]` for interfaces, counters, TCP states, ages, refs, sequence deltas, addresses, ports, ICMP type, pass flags, protocol, version, hash, tag, flags, rule number, group, flags/options/security/auth masks, and ICMP counters.
- `printstatefield()` prints one selected field or all positive fields.

Research notes:
- The `"-"` field has value 31 but no print case, acting as a blank/separator field.
