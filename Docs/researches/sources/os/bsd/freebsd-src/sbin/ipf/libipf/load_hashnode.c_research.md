# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hashnode.c

Hash lookup-table node add/delete helper.

Key behavior:
- Copies family, address, mask, group, and TTL into an `iphtent_t`.
- Uses lookup ioctls to add or delete a node.
- On failure, formats the address/mask into a detailed error message.

Research notes:
- IPv6 mask formatting is suppressed in the error message under `USE_INET6`.
