# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/remque.c

Implements `remque(void *element)` for the legacy `insque`/`remque` doubly linked queue API. It casts the element to an internal two-pointer node and patches neighboring forward/back links if present.

It does not clear the removed element’s own links.
