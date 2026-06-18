# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_binmisc.h

Defines the user/kernel sysctl ABI for miscellaneous binary interpreter image activation. It allows administrators to register interpreter rules keyed by binary magic bytes, optional masks, and offsets, similar in purpose to Linux `binfmt_misc`.

`ximgact_binmisc_entry_t` is versioned and includes flags, magic offset/size, entry name, interpreter path plus arguments, magic bytes, and mask bytes. Limits include 32-byte names, 256-byte magic/mask, 64 entries, and matching only within the first page.

Sysctl names under `kern.binmisc` support add, remove, disable, enable, lookup, and list. User-settable flags enable entries, use masks, and optionally pre-open/cache interpreter vnodes.
