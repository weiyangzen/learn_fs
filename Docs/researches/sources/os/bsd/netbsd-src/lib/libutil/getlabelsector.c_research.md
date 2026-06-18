# File Research: sources/os/bsd/netbsd-src/lib/libutil/getlabelsector.c

## Purpose
Retrieves kernel disklabel placement parameters.

## Key Details
- `getlabelsector()` queries `CTL_KERN/KERN_LABELSECTOR`.
- `getlabeloffset()` queries `CTL_KERN/KERN_LABELOFFSET`.
- `getlabelusesmbr()` queries `kern.labelusesmbr` by name.
- Each returns `-1` on sysctl failure.

## Dependencies and Role
- Disklabel layout support for storage tooling.
