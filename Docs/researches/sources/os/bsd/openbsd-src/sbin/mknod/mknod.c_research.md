# File Research: sources/os/bsd/openbsd-src/sbin/mknod/mknod.c

`mknod.c` implements both `mknod` and `mkfifo`. It pledges `stdio dpath`, parses all arguments into an array of `struct node`, supports `-m mode`, and then creates each requested node with `mknod()`.

For `mkfifo`, all remaining operands become FIFO nodes. For `mknod`, it supports FIFO (`p`), block (`b`), and character (`c`) nodes; block/character devices require major and minor numbers parsed with overflow checks and round-tripped through `makedev()`/`major()`/`minor()`.

Mode handling uses `setmode()`/`getmode()`, forbids bits outside `ACCESSPERMS`, and clears umask only when an explicit mode was provided. Errors creating individual nodes are warned and reflected in the exit status.
