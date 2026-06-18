# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/insque.c

Read completely: 58 lines.

Implements historical `insque(void *entry, void *pred)` for doubly linked queue elements with `q_forw` and `q_back` fields. It inserts `entry` after `pred`, fixing forward and backward links, or initializes `entry` as a standalone element when `pred == NULL`.

The companion `remque()` is elsewhere; this file only inserts.
