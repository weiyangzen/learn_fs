# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/tdelete.c

Implements `tdelete()` for the POSIX binary search tree API. It searches by comparator, unlinks the matching node, handles zero/one/two child cases by promoting the successor when needed, frees the removed node, and updates the caller’s root pointer.

It returns the parent pointer tracked during search, matching the historical API behavior.
