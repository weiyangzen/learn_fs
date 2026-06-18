# File Research: sources/os/bsd/openbsd-src/sbin/savecore/savecore.c

This file implements `savecore`, which locates a kernel crash dump, validates it, writes the vmcore and kernel image to a save directory, optionally compresses them, and clears the dump marker.

Key APIs:
- `main()`: parses `-c`, `-d`/`-v`, `-f`, `-N`, `-z`, sets data rlimit, initializes kvm, unveils paths, validates the dump, saves it, and clears it.
- `kmem_setup()`: reads current kernel symbols, finds dump device/offset/magic, opens block and dump kvm descriptors, validates dump namelist, and accounts for kvm dump header size.
- `check_kmem()`: compares kernel version strings and reads/visualizes panic text.
- `dump_exists()`: compares dump magic and reads dump size.
- `clear_dump()`: invalidates dump state through libkvm.
- `save_core()`: updates `bounds`, writes the core file and kernel file, using `zopen()` when `-z` is set.
- `find_dev()`, `rawname()`: map dump device to `/dev` paths.
- `get_crashtime()`, `check_space()`: validate dump timestamp and save-directory free space/minfree.
- `usage()`: command help.

Behavior and integration:
- Uses libkvm symbols `_dumpdev`, `_dumplo`, `_time_second`, `_dumpsize`, `_version`, `_panicstr`, and `_dumpmag`.
- Writes files named like `/bsd.N.core` and `/bsd.N`, with `.Z` suffix when compressed.
- Reads `/var/crash`-style `bounds` and `minfree` files.
- Applies `unveil()` and `pledge()` after discovering the needed kernel/dump paths.
- Logs via syslog and prints progress while copying dump data.

Risk notes:
- `bounds` is incremented before later copy operations, intentionally avoiding overwrite but leaving gaps after failures.
- The dump copy path exits on incomplete reads/writes and warns that the core may be incomplete.
- `rawname()` allocates a new string each call and is used for path setup in a short-lived process.
