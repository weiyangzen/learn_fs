# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fs.c

This file exposes `5e` emulator processes through a proc-like 9P filesystem.

Main structures:
- Defines qid IDs for proc entries such as `args`, `ctl`, `fd`, `fpregs`, `kregs`, `mem`, `note`, `regs`, `segment`, `status`, `text`, `wait`, `profile`, and `syscall`.
- `Dirtab procdir[]` lists supported entries, permissions, and nominal sizes.
- `Aux` stores selected `Process`, opened fd, and directory entry for a fid.

Main behavior:
- `readin()` reads data from the host `/proc/<pid>/<file>`.
- `calcmem()` computes non-stack memory usage in KB.
- `copymem()` copies bytes from emulator segments for `mem` reads.
- `segments()` formats segment layout/refcount info.
- 9P callbacks:
  - `procattach()` initializes root fid aux state.
  - `procwalk()` walks root pid directories and per-process entries.
  - `procclone()` copies fid aux.
  - `procopen()` opens the process text file for `text`.
  - `procdestroyfid()` frees aux state.
  - `procgen()` and `procsubgen()` enumerate process and file directories.
  - `procread()` serves directory listings, `status`, `segment`, `text`, `mem`, and `regs`.
  - `procwrite()` proxies writes to host `/proc/<pid>/note` for `note`.
  - `procstat()` fills directory metadata.
- `initfs()` posts and mounts the service at the requested mount point.

Dependencies and interactions:
- Enabled by `5e -p`, called from `5e.c`.
- Reads emulator state directly and delegates unsupported proc entries to placeholder errors.

Research relevance:
- Bridges emulator state to Plan 9 tooling through a familiar `/proc` surface.

Risk notes:
- Many listed proc entries are not actually readable/writable beyond the handled cases.
- `copymem()` walks segments without segment locks.
- `procwrite()` is present but not installed in `procsrv`, which only sets attach/walk/clone/destroyfid/open/read/stat.
