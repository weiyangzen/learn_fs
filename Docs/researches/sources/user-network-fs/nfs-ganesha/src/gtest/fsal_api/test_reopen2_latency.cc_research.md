# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_reopen2_latency.cc

## Purpose
This test benchmarks changing open mode on an already opened FSAL file via `reopen2`. It exercises both direct object operations and the `fsal_reopen2` wrapper.

## Important APIs, Types, And Functions
`Reopen2EmptyLatencyTest` allocates a share state with `alloc_state`, opens `test_file` using `obj_ops->open2` with `FSAL_O_RDWR`, closes with `close2`, and releases the state with `free_state`. Tests call `obj_ops->reopen2`, `fsal_reopen2`, and bypass `sub_hdl->obj_ops->reopen2`.

## Control Flow, State, And Persistence
Setup creates and opens a file under `reopen2_latency`. `SIMPLE` reopens it as read-only once. Loop tests run one million iterations, alternating `FSAL_O_READ` and `FSAL_O_WRITE` to force real mode transitions. Teardown closes the file with the same state, removes it, releases the object reference, and removes the test root.

## Dependencies And Integration Points
The file depends on FSAL state management, open2/reopen2/close2 object semantics, MDCACHE debug access, and shared Ganesha setup. It is sensitive to whether the sub-handle implementation accepts the same state object allocated from the outer export.

## Risks And Test Signals
Alternating modes is a useful signal for catching no-op reopen paths, but the tests do not verify access mode after each call. Bypass tests may mix MDCACHE and sub-FSAL state assumptions. Correctness is limited to `status.major == 0` plus teardown success.
