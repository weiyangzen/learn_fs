# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/nat_setgroupmap.c

NAT group-map port/address distribution calculator.

Key behavior:
- Computes `in_ippip`, `in_ppip`, `in_space`, and related fields based on original/new source masks.
- Handles equal masks, automatic port mapping, and explicit per-IP port allocation.

Research notes:
- Uses `USABLE_PORTS` and mask arithmetic in host byte order.
