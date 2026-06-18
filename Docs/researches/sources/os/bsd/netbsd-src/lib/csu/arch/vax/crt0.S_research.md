# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crt0.S

VAX process entry stub. It pushes `%r9` as `ps_strings`, pushes `%r7` as cleanup, and calls `___start` with two arguments.

The entry mask is zero, so no registers are automatically saved.
