# File Research: sources/virtualization/libguestfs/daemon/zerofree.c

## Role
Wraps the external `zerofree` utility.

## Main Operations
- `optgroup_zerofree_available()` checks for `zerofree`.
- `do_zerofree()` runs `zerofree <device>` and reports command errors.

## Filesystem/Storage Relevance
`zerofree` zeroes unused blocks in supported filesystems, improving sparsification and compressed image efficiency.
