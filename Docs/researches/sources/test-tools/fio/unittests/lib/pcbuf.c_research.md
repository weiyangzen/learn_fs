# sources/test-tools/fio/unittests/lib/pcbuf.c

Purpose: CUnit tests for fio's producer/consumer circular buffer (`pcbuf.h`) using a deliberately small capacity to exercise full, empty, commit, and wrap-around behavior.

Important APIs/functions: `test_pcbuf_basic_ops()` allocates a buffer, checks initial state, stages `capacity - 1` values, verifies the reserved-slot full condition, commits, pops values in FIFO order, and checks empty state. `test_pcbuf_wraparound()` commits near-capacity data, pops one element, stages another value to wrap, then verifies the remaining sequence.

Control flow/state: staged entries are invisible to committed pop size until `pcb_commit()`. The tests explicitly distinguish `pcb_staged_size()` from `pcb_committed_size()`.

Dependencies/integration: includes `pcbuf.h` from the unit-test lib directory and CUnit wrappers.

Risks/test signals: strong regression coverage for ring-index arithmetic. Missing coverage includes allocation failure, multiple commits without pops, staged rollback if supported elsewhere, and concurrent producer/consumer use.
