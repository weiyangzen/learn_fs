# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tfind.c

Implements `tfind()` for the POSIX binary search tree API. It walks left or right according to the comparator until it finds a matching key and returns the node pointer, or returns NULL if the tree/root is absent or no key matches.

No allocation or mutation occurs.
