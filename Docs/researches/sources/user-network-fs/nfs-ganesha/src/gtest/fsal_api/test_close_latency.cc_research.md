<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc

Purpose: latency/correctness benchmark for legacy/helper `fsal_close`.

Important APIs/types/functions: uses `fsal_open2` to create/open files, `fsal_close` for the measured operation, `fsal_remove` for cleanup, and object `put_ref` after removal. Fixture derives from `GaneshaFSALBaseTest`; `CloseFullLatencyTest` can prime many entries but the listed tests use the empty fixture.

Control flow/state: `SIMPLE` opens one file, closes it, removes it, and releases the object. `LOOP` opens 100000 files first, times only `fsal_close` over the object array, then removes and releases each file. Persistent state is in the configured export; test state is arrays of handles.

Dependencies/integration: embedded Ganesha test environment, FSAL open/close/remove helper APIs, and a writable export. CLI parsing supports config/log/debug/export/session/event-list/profile but this file does not use event/profile hooks in test bodies.

Risks: `LOOP_COUNT` must be lower than available file descriptor/state limits, as the file comment notes. Failures during the open phase can leave created files until fixture/environment teardown.

Test signals: status major equals zero for open, close, and remove; stderr prints average `fsal_close` latency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_close_latency.cc -->
