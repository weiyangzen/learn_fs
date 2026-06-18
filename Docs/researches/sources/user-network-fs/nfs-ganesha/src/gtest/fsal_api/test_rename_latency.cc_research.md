# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_rename_latency.cc

## Purpose
This executable benchmarks FSAL rename operations for an individual file in empty and populated directories. It compares direct object operations, the `fsal_rename` wrapper, and MDCACHE bypass sub-handles.

## Important APIs, Types, And Functions
Fixtures derive from `GaneshaFSALBaseTest`; `RenameFullLatencyTest` adds 100,000 primed entries. Tests use `fsal_create`, `obj_ops->rename`, `fsal_rename`, `obj_ops->lookup`, `fsal_remove`, and `mdcdb_get_sub_handle`. File names are held in fixed `NAMELEN` buffers and generated with `sprintf("nf-%08x", i)`.

## Control Flow, State, And Persistence
Simple tests create `original_name`, rename it to `new_name`, verify lookup returns the same handle, then remove it. Loop tests create one file and repeatedly rename that single object to a new name, updating the current-name buffer after each successful call. Full tests do the same while extra directory entries exist. Teardown for full tests removes the primed entries after the benchmark-created file is cleaned up.

## Dependencies And Integration Points
The file exercises FSAL rename semantics, wrapper-vs-object-operation layering, MDCACHE bypass handling, and directory lookup behavior. It uses the shared test root named `test_root`, which is generic and may be less distinctive than other latency tests.

## Risks And Test Signals
The loop uses `sprintf`/`strncpy` into `NAMELEN` buffers; current generated names fit, but changing name formats could truncate. `SIMPLE_BYPASS` compares lookup and sub-handle object pointers, which depends on bypass identity behavior. The main correctness signals are successful rename status and lookup identity in simple cases; loop tests assert status and leave cleanup dependent on the last tracked filename.
