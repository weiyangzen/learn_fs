# sources/sync-backup/rsync/testsuite/acls-depth_test.py

Purpose: depth companion for `-A`; it checks that a distinctive POSIX ACL is preserved on every file and directory in a tree at least three levels deep.

Important APIs/types/functions: `make_tree`, `walk_dirs`, `walk_files`, `run_rsync('-aA')`, direct `setfacl` and `getfacl`, local `getfacl(path)` normalizer, and `test_fail`/`test_skipped`.

Control flow: skip unless rsync advertises ACL support and `setfacl`/`getfacl` exist. Build a depth-3 tree, apply `u:0:r-x` to every entry, sync with `-aA`, then compare normalized getfacl output for every relative path.

State and persistence behavior: source ACLs are durable filesystem metadata and are expected to appear identically on destination paths. Path-dependent getfacl comments are stripped before comparison.

Dependencies and integration points: POSIX ACL filesystem support, external ACL commands, and rsync archive ACL preservation.

Risks and test signals: skips if ACLs cannot be set. Failure indicates ACL loss at depth, identity-name rendering issues beyond accepted root/0 spelling, or resolver/path traversal regressions for deep ACL metadata.
