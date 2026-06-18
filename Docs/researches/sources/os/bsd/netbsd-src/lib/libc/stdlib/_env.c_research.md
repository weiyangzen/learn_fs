# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/_env.c

Read completely: 404 lines.

Implements internal environment storage support. It tracks environment strings allocated by libc in an address-keyed red-black tree, tracks a libc-owned `environ` array, and provides helpers for validating variable names, allocating/freeing environment strings, testing whether a variable can be overwritten in place, finding slots, and finding variable values.

`__getenvslot()` searches existing entries by name, optionally grows or creates the environment array with `reallocarr()`, copies foreign `environ` arrays into libc-owned storage, and scrubs stale allocated variables. `__scrubenv()` marks currently referenced environment strings and frees unreferenced tracked strings.

Threaded builds expose `__readlockenv()`, `__writelockenv()`, and `__unlockenv()` around a static rwlock. The obsolete `__findenv()` compatibility interface validates the name, returns the value pointer, and writes the integer offset.
