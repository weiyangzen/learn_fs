# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devarch.c

Plan 9 `#P/arch` device for Tegra-specific architecture files.

Key responsibilities:
- Maintains a small dynamic directory of architecture files with per-file read/write callbacks.
- Provides `addarchfile` for other architecture code to register files.
- Implements standard Plan 9 device operations for attach, walk, stat, open, close, read, and write.
- Registers `cputype` and `timebase` in `archinit`.
- Reports CPU type/frequency through `cputyperead`.
- Reports cycle/timebase value through `tbread`; an `nsec` reader exists but is not registered.

Dependencies and assumptions:
- Depends on Plan 9 device helpers, `cputype2name`, `cycles`, and global `m`.
- Directory capacity is fixed at `Qmax` 16 entries.

Notable risks:
- Added files cannot be removed, and duplicate names are rejected.
- `nsread` uses a fixed conversion expression and is commented out from registration.
