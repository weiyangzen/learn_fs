# File Research: sources/os/bsd/openbsd-src/sys/sys/filedesc.h

This header defines per-process/shared file descriptor table structures and descriptor-management APIs.

Key definitions:
- Sizing constants: `NDFILE`, `NDEXTENT`, `NDENTRIES`, `NDENTRYMASK`, `NDENTRYSHIFT`, `NDREDUCE`, `NDHISLOTS`, `NDLOSLOTS`.
- `struct filedesc` with open file pointer array, per-fd flags, cwd/root vnodes, allocation/open counters, free-fd bitmaps, umask, refcount, rwlock, file-pointer mutex, attached kqueues, flags, and kqueue user-event count.
- `struct filedesc0` embeds initial storage for the first descriptors and bitmap arrays.
- Per-fd flags: `UF_EXCLOSE`, `UF_PLEDGED`, `UF_FORKCLOSE`, `UF_PLEDGEOPEN`.
- Descriptor-table flag: `FD_ADVLOCK`.
- `OFILESIZE`.

Kernel APIs:
- Lifecycle/copy/share/free: `filedesc_init`, `fdinit`, `fdshare`, `fdcopy`, `fdfree`.
- Allocation/insert/remove/release: `fdalloc`, `fdexpand`, `falloc`, `fnew`, `fdinsert`, `fdremove`, `fdrelease`, `dupfdopen`.
- Exec/fork helpers: `fdprepforexec`.
- Lookup/iteration: `fd_iterfile`, `fd_getfile`, `fd_getfile_mode`, `fd_checkclosed`.
- Close/socket helpers: `closef`, `getsock`.
- Lock macros: `fdplock`, `fdpunlock`, `fdpassertlocked`.

Risk notes:
- Descriptor flags include both close-on-exec and close-on-fork behavior.
- `fd_ofiles` access is protected by two different locks depending on operation mode; misuse can race descriptor table expansion or closure.
