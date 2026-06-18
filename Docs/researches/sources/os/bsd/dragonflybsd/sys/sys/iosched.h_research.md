# File Research: sources/os/bsd/dragonflybsd/sys/sys/iosched.h

`iosched.h` defines small I/O scheduler accounting structures and kernel hooks. Kernel/structure builds include type, queue, and systimer headers.

`struct iosched_data` records read bytes, write bytes, and the last tick value used for decay/accounting.

Under `_KERNEL`, it forward-declares `struct thread` and declares `bwillwrite()`, `bwillread()`, `bwillinode()`, and `biosched_done()`. This is a compact interface between buffer/cache I/O paths and scheduler accounting.
