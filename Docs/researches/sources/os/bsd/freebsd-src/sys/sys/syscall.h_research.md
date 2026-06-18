# File Research: sources/os/bsd/freebsd-src/sys/sys/syscall.h

## Purpose
`syscall.h` is the generated FreeBSD system call number table.

## Main Interfaces
- Maps syscall names to numeric IDs from `SYS_syscall` 0 through `SYS_renameat2` 602.
- Defines `SYS_exit` as `SYS__exit`.
- Includes active, compatibility, obsolete-commented, and FreeBSD-versioned syscall names.
- Filesystem/VFS-relevant entries include `mount`, `unmount`, `stat`, `fstat`, `statfs`, `getfsstat`, `fhopen`, `fhstat`, `openat`, `linkat`, `renameat`, `unlinkat`, `copy_file_range`, `fspacectl`, `getfhat`, `fhlink`, `funlinkat`, and many compatibility forms.
- Defines `SYS_MAXSYSCALL` as 603.

## Implementation Notes
The file is marked automatically generated and should not be edited directly. Commented holes preserve historical syscall number positions.

## Dependencies and Constraints
No includes. ABI stability depends on syscall numbers remaining consistent with the generated syscall switch, libc stubs, and syscall object list.
