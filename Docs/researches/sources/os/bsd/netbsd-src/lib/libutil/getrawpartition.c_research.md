# File Research: sources/os/bsd/netbsd-src/lib/libutil/getrawpartition.c

## Purpose
Returns the kernel raw partition index.

## Key Details
- Queries `CTL_KERN/KERN_RAWPARTITION`.
- Returns raw partition number or `-1` on sysctl failure.

## Dependencies and Role
- Used by `opendisk.c` to append the default raw partition letter.
