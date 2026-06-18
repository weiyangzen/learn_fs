# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_lookup_latency.cc

## Purpose
This test benchmarks the NFSv4 `LOOKUP` operation handler for both the per-test root and entries in a large populated directory. It validates that the handler updates compound current object state to the expected FSAL handle.

## Important APIs, Types, And Functions
Fixtures derive from `GaeshaNFS4BaseTest`; `LookupFullLatencyTest` creates 100,000 files and stores handles in `objs`. Tests use `setup_lookup`, `cleanup_lookup`, `setCurrentFH`, `nfs4_op_lookup`, `enableEvents`, optional profiler calls, and comparisons against `data->current_obj`.

## Control Flow, State, And Persistence
`SIMPLE` and `LOOP` set the current file handle to `root_entry` and look up `TEST_ROOT`. Full tests set current file handle to `test_root` and look up generated names `f-%08x`. The big loop rebuilds the lookup name each iteration, cycles through all stored handles, validates `NFS4_OK`, checks current object identity, and cleans the lookup argument.

## Dependencies And Integration Points
The test integrates direct NFSv4 handler invocation with FSAL handles created by the base fixture. It uses the generated naming convention from `create_and_prime_many` and optional LTTng/gperftools instrumentation.

## Risks And Test Signals
Object identity checks depend on cached handles matching those stored during setup. Repeated direct operation calls can accumulate response state if handler allocation is not idempotent until fixture teardown. The strongest signals are `NFS4_OK`, exact `data->current_obj` comparison, and successful full cleanup.
