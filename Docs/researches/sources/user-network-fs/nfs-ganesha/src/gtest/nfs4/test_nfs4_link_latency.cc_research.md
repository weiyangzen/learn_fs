# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_link_latency.cc

## Purpose
This NFSv4 latency test measures the `LINK` operation handler by creating hard links to existing objects in a populated test directory. It invokes `nfs4_op_link` directly with prepared compound current and saved file handles.

## Important APIs, Types, And Functions
`LinkFullLatencyTest` derives from `GaeshaNFS4BaseTest`, creates 100,000 files into `objs`, and calls `set_saved_export`. Tests use `setup_link`, `setCurrentFH(test_root)`, `setSavedFH(objs[n])`, `nfs4_op_link`, `cleanup_link`, `fsal_remove`, `enableEvents`, `disableEvents`, and optional `ProfilerStart/ProfilerStop`.

## Control Flow, State, And Persistence
`BIG_SINGLE` creates one new hard link for `objs[DIR_COUNT / 5]`, measures a single call, and removes the link. `BIG` loops one million times, cycling source objects and generating link names `d-%08x-%08x`; cleanup removes every created link after timing. Fixture teardown removes the original primed files.

## Dependencies And Integration Points
The test depends on NFSv4 compound state from `gtest_nfs4.hh`, FSAL hard-link support, LTTng event controls, gperftools, and Ganesha FSAL cleanup. The saved file handle identifies the existing source object; current file handle identifies the destination directory.

## Risks And Test Signals
The test creates one million hard links, which can exceed filesystem limits or make cleanup expensive. It does not call `nfs4_Compound_FreeOne` inside the loop, so handler response ownership must remain safe for repeated direct calls or be handled by the fixture teardown. The primary signals are `NFS4_OK` per operation, timing output, profiling traces, and successful removal of created links.
