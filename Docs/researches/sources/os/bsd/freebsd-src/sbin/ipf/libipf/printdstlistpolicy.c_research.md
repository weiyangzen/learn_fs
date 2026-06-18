# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlistpolicy.c

Destination-list policy name printer.

Key behavior:
- Maps `IPLDP_NONE`, `IPLDP_ROUNDROBIN`, `IPLDP_CONNECTION`, and `IPLDP_RANDOM` to text.

Research notes:
- Unknown policies print nothing.
