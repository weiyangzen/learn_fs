# File Research: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/mksnap_ffs.c

## Summary
Creates an FFS/UFS snapshot file by issuing an `nmount()` update request with the `snapshot` option, then adjusts ownership and permissions.

## Main Responsibilities
- Accepts current `snapshot_name` usage and old three-argument compatibility form.
- Validates snapshot path length, parent directory existence, directory type, write permission, and sticky-bit constraints.
- Handles chroot edge cases where `f_mntonname` may point outside the visible root by finding a same-filesystem path suffix.
- Builds `nmount` iovecs for `fstype=ffs`, `from=snapshot`, `fspath=mountpoint`, `update`, and `snapshot`.
- Verifies created file has `SF_SNAPSHOT`.
- Sets group to `operator` and mode to user/group read.

## Key Functions
- `isdir()`: stat and directory check.
- `issamefs()`: compares filesystem IDs for mountpoint suffix detection.
- `main()`: permission checks, snapshot mount update, post-create validation and chmod/chown.

## Dependencies And Integration
Uses UFS/FFS mount semantics via `nmount()`, `build_iovec`, `statfs`, file flags, and the `operator` group.

## Research Notes
Most safety logic occurs before `nmount`: the program checks that the invoking user can create and later remove the snapshot file in the target directory.
