# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolnode.c

Pool node formatter.

Key behavior:
- Field mode delegates to `printpoolfield()`.
- Normal mode prints optional negation, address, and mask.
- Debug mode prints address, mask, hits, bytes, name, and refcount.

Research notes:
- Returns the node’s `ipn_next` pointer to drive callers’ list traversal.
