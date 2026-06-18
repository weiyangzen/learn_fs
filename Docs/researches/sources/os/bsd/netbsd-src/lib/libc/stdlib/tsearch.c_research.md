# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tsearch.c

Implements `tsearch()`, the find-or-insert binary search tree operation. It searches by comparator and returns an existing node on equality; if absent, it allocates a `node_t`, stores the key pointer, initializes child links to NULL, and links it into the tree.

If allocation fails, it returns NULL and leaves the tree unchanged.
