# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devarch.c

Implements Plan 9 architecture device `#P`.

Key behavior:
- Maintains a small static `archdir` namespace with dynamic file registration through `addarchfile()`.
- `addarchfile()` prevents duplicate names, assigns qid paths, and records read/write callbacks.
- Standard dev methods support attach, walk, stat, open, close, read, and write.
- Directory reads go through `devdirread`; file reads/writes dispatch to registered callbacks or return `Eperm`.
- `archinit()` registers a read-only `cputype` file.
- `cputyperead()` returns `ARM11 <MHz>` based on `m->cpumhz`.

This is the platform-specific control/status filesystem hook for small architecture properties.
