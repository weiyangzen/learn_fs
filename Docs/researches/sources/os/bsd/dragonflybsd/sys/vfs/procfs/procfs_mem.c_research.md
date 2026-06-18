# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_mem.c

This file implements `/proc/<pid>/mem` read/write access to a target process address space. `procfs_rwmem()` validates that the process is not exiting, execing, zombie, or in early allocation state, holds the vmspace, allocates one pageable kernel page of KVA, faults one target page at a time with read or write permissions, maps it into kernel space with quick pmap functions, and copies through `uiomove()`.

`procfs_domem()` wraps this with authorization: zero-length I/O succeeds, execing targets return `EAGAIN`, and unauthorized or jail-crossing access returns `EPERM`.

`procfs_findtextvp()` returns `p_textvp`, though comments note `/proc/pid/file` has information-leak concerns.

Research notes: the read/write implementation intentionally operates page-by-page. A comment warns about potential deadlock around busy pages on write faults.
