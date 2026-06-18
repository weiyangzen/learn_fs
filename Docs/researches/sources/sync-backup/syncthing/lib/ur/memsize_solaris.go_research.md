# sources/sync-backup/syncthing/lib/ur/memsize_solaris.go

Purpose: Solaris implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` obtains page size through `unix.Getpagesize`, gets physical page count with `unix.Sysconf(unix.SC_PHYS_PAGES)`, and returns pages multiplied by page size. Errors return zero.

State and persistence: no state.

Dependencies and integration: uses `golang.org/x/sys/unix`; feeds usage report memory size.

Risks: multiplication could overflow only on unrealistic values before conversion context; syscall errors silently become zero. No tests in this subset.
