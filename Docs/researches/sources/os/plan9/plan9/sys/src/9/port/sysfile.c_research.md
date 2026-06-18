# File Research: sources/os/plan9/plan9/sys/src/9/port/sysfile.c

Implements file, fd, directory, mount, and stat-related syscalls.

File descriptor management:
- `growfd`, `findfreefd`, `newfd`, `newfd2`, `fdtochan`, `fdclose`, `sysdup`, `sysclose`, `sysfd2path`.
- Enforces mode checks, close-on-exec flags, and descriptor-table growth in `DELTAFD` chunks with a hard practical cap.

Open/create/pipe:
- `sysopen`, `syscreate`, `syspipe`.
- `openmode` validates and normalizes Plan 9 open modes.

Read/write:
- Internal `read` supports normal read and pread-style fixed offset.
- Internal `write` supports normal write and pwrite-style fixed offset.
- `sys_read`, `syspread`, `sys_write`, `syspwrite` expose old and pread/pwrite variants.
- Directory reads are postprocessed through union reads and mount rewriting.

Directory/mount rewriting:
- `unionread` reads across union mount chains.
- `unionrewind`, `mountrewind`, `mountrock`, and `mountrockread` preserve directory-entry continuity when mount rewriting changes entry sizes.
- `mountfix` replaces directory entries corresponding to current mount points with stat data for mounted targets while preserving original names.

Seek/stat/wstat:
- `sysseek` and `sysoseek` implement 64-bit and old seek.
- `validstat` checks stat buffer structure and validates names.
- `sysstat`, `sysfstat`, `syswstat`, `sysfwstat`.
- Old compatibility calls `sys_stat`, `sys_fstat`, `sys_wstat`, `sys_fwstat` convert or reject old formats.

Namespace operations:
- `bindmount` implements both bind and mount common logic.
- `sysbind`, `sysmount`, `sys_mount`, `sysunmount`.
- Mounting uses devmnt attach with channel/auth/spec metadata.
- Removing or renaming mount points is disallowed to avoid ambiguity.

Other:
- `syschdir` replaces `up->dot`.
- `sysremove` handles remove semantics where remove clunks the fid, then neutralizes channel close.

Role:
- Core Plan 9 syscall bridge between fd/name APIs and device `Dev` methods.
