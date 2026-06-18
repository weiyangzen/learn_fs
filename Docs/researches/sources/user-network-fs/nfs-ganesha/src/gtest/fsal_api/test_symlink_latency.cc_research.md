# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_symlink_latency.cc

## Purpose
This test benchmarks creating symbolic links through direct object operations and the `fsal_create` wrapper. It also verifies simple created-link lookup and target content.

## Important APIs, Types, And Functions
The fixture creates an initial `test_symlink` pointing at `TEST_ROOT` so expected content is available in `bfr_content`. Tests use `obj_ops->symlink`, `fsal_create(..., SYMBOLIC_LINK, ...)`, `obj_ops->lookup`, `obj_ops->readlink`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`.

## Control Flow, State, And Persistence
Setup creates a baseline symlink under `root_entry`, reads its content, and stores the returned buffer. Simple tests create `symlink_to_symlink_latency`, verify lookup identity, read and compare target content, free the returned target, release handles, and remove the created link. Loop tests create one million uniquely named symlinks and then remove them in a second loop. Full tests do the same while a 100,000-file test root exists.

## Dependencies And Integration Points
The file exercises root-level symlink creation rather than creation inside `test_root`, and depends on Ganesha memory ownership for readlink buffers. Bypass tests use sub-root handles and refresh the root entry via `nfs_export_get_root_entry`.

## Risks And Test Signals
Creating and removing one million symlinks is expensive and may leave large cleanup work after failure. The bypass simple path compares a lookup from `root_entry` with a symlink created through a sub-handle, which may not have identical object identity across stack layers. Correctness signals include lookup identity, target byte comparison, status checks, and cleanup success.
