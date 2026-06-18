# File Research: sources/os/bsd/netbsd-src/lib/libutil/kinfo_getvmmap.c

## Purpose
Returns a process VM map snapshot.

## Key Details
- Builds `CTL_VM/VM_PROC/VM_PROC_MAP/<pid>/<entry-size>` sysctl MIB.
- First sysctl gets required length.
- Allocates 4/3 of that size to reduce race risk.
- Second sysctl fills an array of `struct kinfo_vmentry`.
- Sets `*cntp` to entry count; caller must free the returned array.

## Dependencies and Role
- Process introspection utility.
