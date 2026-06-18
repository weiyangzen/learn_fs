# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_putfh_latency.cc

## Purpose
This NFSv4 test measures the `PUTFH` operation handler, which sets the compound current file handle and current object. It covers one root object, one populated-file object, and a one-million-iteration loop over many file handles.

## Important APIs, Types, And Functions
`PutfhEmptyLatencyTest` uses the base compound fixture without extra entries. `PutfhFullLatencyTest` stores 100,000 created file handles. Tests call `setup_putfh`, `cleanup_putfh`, `nfs4_op_putfh`, and compare `data->current_obj` with the expected FSAL object.

## Control Flow, State, And Persistence
`SIMPLE` prepares a PUTFH argument for `test_root`, executes one handler call, and checks success/current object. `LOOP` reuses the same PUTFH argument for one million calls. Full tests generate a new serialized file handle for each selected object and clean it after each big-loop iteration. Fixture teardown frees compound/XDR allocations and removes all test files.

## Dependencies And Integration Points
The file depends on `nfs4_FSALToFhandle` through the setup helper, NFSv4 handler state in `compound_data_t`, the shared FSAL test root, LTTng event controls, and gperftools profiling.

## Risks And Test Signals
The big loop repeatedly allocates and frees NFSv4 file-handle buffers, so it measures both handler cost and argument setup overhead inside the timed region. The empty loop reuses one handle, giving a different signal. Assertions on `data->current_obj` are important for catching stale or failed handle resolution.
