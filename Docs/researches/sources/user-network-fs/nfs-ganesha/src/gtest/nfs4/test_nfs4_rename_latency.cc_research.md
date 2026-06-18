# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_rename_latency.cc

## Purpose
This test benchmarks the NFSv4 `RENAME` operation handler for the per-test root and for entries in a large directory. It uses prepared current and saved file handles as source and destination directories.

## Important APIs, Types, And Functions
`RenameFullLatencyTest` derives from `GaeshaNFS4BaseTest`, creates 100,000 file handles, and calls `set_saved_export`. Tests use `setup_rename`, `swap_rename`, `cleanup_rename`, `setCurrentFH`, `setSavedFH`, `nfs4_op_rename`, LTTng event controls, and optional profiler calls.

## Control Flow, State, And Persistence
Empty tests rename the test root between `nfs4_rename_latency` and `nfs4_rename_latency2`, swapping names so the final state is restored. Full single test renames one file to an `r-%08x` name, measures one operation, then swaps it back. The big loop cycles through all files and alternates direction per full pass over the file set so names remain recoverable for teardown.

## Dependencies And Integration Points
The test exercises NFSv4 rename semantics directly, while relying on FSAL object setup, export references, and generated file naming from `create_and_prime_many`. It integrates with LTTng/gperftools instrumentation in the same way as the other NFSv4 latency tests.

## Risks And Test Signals
Renaming the fixture's own test root in empty tests is sensitive because base teardown expects the original root name; the even loop count and explicit swap-back are essential. Failure mid-loop may leave files under `r-*` names, causing `remove_many` to miss them. Signals are `NFS4_OK`, timing, and successful restoration/cleanup.
