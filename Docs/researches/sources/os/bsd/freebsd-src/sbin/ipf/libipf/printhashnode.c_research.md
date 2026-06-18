# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashnode.c

Hash lookup-table node formatter.

Key behavior:
- Copies one `iphtent_t` through the supplied copy function.
- Field mode prints selected pool/hash fields.
- Debug mode prints hash bucket, address/mask, refs, group, hits, and bytes.
- Normal mode prints address/mask and optional group-map override.

Research notes:
- Hash bucket calculation uses the IPv4 hash macro even before family-specific printing.
