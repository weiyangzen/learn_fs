# File Research: sources/os/bsd/netbsd-src/lib/libutil/getmaxpartitions.c

## Purpose
Returns the kernel maximum partition count.

## Key Details
- Queries `CTL_KERN/KERN_MAXPARTITIONS`.
- Returns the count or `-1` on failure.

## Dependencies and Role
- Storage utility for tools that need kernel partition table limits.
