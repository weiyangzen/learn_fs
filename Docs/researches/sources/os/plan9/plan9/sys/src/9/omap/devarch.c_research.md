# File Research: sources/os/plan9/plan9/sys/src/9/omap/devarch.c

Implements the OMAP `#P/arch` device and CPU/timebase arch files.

Key points:
- Maintains a small dynamic `archdir` table with per-file read/write function arrays.
- `addarchfile()` adds permanent files under `#P`, rejects duplicates, and assigns qid paths.
- Implements standard Plan 9 device methods for attach, walk, stat, open, close, read, and write.
- `archread()` dispatches per-file reads through the registered function pointer; `archwrite()` dispatches writes similarly.
- `cputype2name()` returns `Cortex-A8`.
- Adds `cputype` and `timebase` in `archinit()`.
- `cputyperead()` reports ARM CPU type and current MHz.
- `tbread()` reports `cycles()` as a hex timebase value.
- `nsread()` exists but is not registered.

Dependencies and interactions:
- `cpuidprint()` in `archomap.c` calls `cputype2name()`.
- Portable dev interfaces use `archdevtab`.
- Other arch code can publish files with `addarchfile()`.

Research relevance:
- Minimal machine introspection filesystem for the OMAP kernel.
