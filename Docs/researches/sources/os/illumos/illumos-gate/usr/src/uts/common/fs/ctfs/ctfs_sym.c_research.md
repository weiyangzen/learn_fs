# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_sym.c

This file implements ctfs symbolic-link vnodes for `/system/contract/all/<ctid>`. The symlink points from the aggregate `all` contract directory back to the typed contract directory, using a target of the form `../<type>/<id>`.

Key routines:
- `ctfs_create_symnode()` creates a GFS file vnode, marks it `VLNK`, stores the contract pointer, formats and stores the symlink target string, and takes a contract hold.
- `ctfs_sym_getattr()` reports a read-only symlink with size equal to the symlink target length and timestamps derived from the contract creation time.
- `ctfs_sym_readlink()` returns the prebuilt target through `uiomove()`.
- `ctfs_sym_inactive()` releases the held contract and frees the symlink string and node storage after `gfs_file_inactive()` confirms teardown.

The vnode operation table exposes open, close, getattr, readlink, read-only access, and inactive handling. Directory operations are rejected with `fs_notdir`; ioctl is invalid.

Integration points are `gfs_file_create()`, `ctfs_ops_sym`, `contract_hold()`, `contract_rele()`, `ctfs_common_getattr()`, and standard VOP dispatch through `ctfs_tops_sym`.

Primary correctness concerns are lifetime symmetry between `contract_hold()` and `contract_rele()`, and keeping `ctfs_sn_size` consistent with the allocated symlink string length.
