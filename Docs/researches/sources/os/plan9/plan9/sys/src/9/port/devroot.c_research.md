# File Research: sources/os/plan9/plan9/sys/src/9/port/devroot.c

Implements `#/`, the synthetic root device. It provides a fixed initial root namespace plus a `boot` directory containing boot-time files added by the kernel.

`rootdir` starts with `#/` and `boot`; `rootreset` adds standard directories such as `bin`, `dev`, `env`, `fd`, `mnt`, `net`, `net.alt`, `proc`, `root`, and `srv`. `bootlist` starts with its directory entry, and `addbootfile` appends named immutable boot files with content pointers and lengths.

`Dirlist` tracks a base qid path, `Dirtab` array, data pointer array, current count, and max count. `addlist` assigns qids sequentially, records permissions, and marks directory qids when needed.

`rootgen` enumerates root and boot directories and handles dot-dot behavior. `rootread` serves directory reads or copies bytes from in-memory boot/root file data. Writes always fail.

This device is the seed namespace for early system operation, before normal filesystem mounts populate standard directories.
