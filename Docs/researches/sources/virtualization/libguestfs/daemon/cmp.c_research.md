# File Research: sources/virtualization/libguestfs/daemon/cmp.c

Implements file equality testing.

Key points:
- `do_equal` maps both guest paths through `sysroot_path`.
- Runs `cmp -s file1 file2`.
- Returns boolean true for exit `0`, false for exit `1`, and daemon error for execution failure or unexpected status.
