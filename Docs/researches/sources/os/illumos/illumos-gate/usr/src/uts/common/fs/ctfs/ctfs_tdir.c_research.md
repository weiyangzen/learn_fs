# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tdir.c

This file implements ctfs per-contract-type directories, such as `/system/contract/<type>`. Each directory contains fixed control entries and dynamically enumerated contract ID directories.

Static entries are:
- `bundle`
- `pbundle`
- `template`
- `latest`

Key routines:
- `ctfs_create_tdirnode()` creates a GFS directory with the static entry table plus custom inode, readdir, and lookup callbacks.
- `ctfs_tdir_getattr()` reports a read-only directory, link count based on fixed entries, and size based on fixed entries plus the contract count for the type.
- `ctfs_tdir_do_inode()` maps each fixed entry index into a ctfs type-file inode.
- `ctfs_tdir_do_readdir()` enumerates contract IDs visible in the vnode’s zone by using `contract_type_lookup()` and emits numeric directory names.
- `ctfs_tdir_do_lookup()` parses a numeric name, resolves the matching contract with `contract_type_ptr()`, creates a contract directory vnode, and releases the contract reference after vnode creation.

The implementation is zone-aware through `VTOZONE(vp)->zone_uniqid`. It depends on `ct_types[gfs_file_index(vp)]` to map the GFS file index to a contract type.

The vnode operation table delegates readdir and lookup to generic GFS helpers and marks the directory read/search-only. Correctness depends on contract lookup/release balance and numeric-name parsing rejecting suffixes.
