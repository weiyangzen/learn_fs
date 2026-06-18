# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_trace_apply.rs

## Purpose
This file is a placeholder failpoint test module for trace-apply recovery scenarios. It currently contains TODO comments only.

## Important APIs, Types, and Functions
There are no APIs or tests. The TODO list names planned coverage: recovery when split has not started, split has not finished, two pending splits where the second finishes before the first, and all splits finished.

## Control Flow
No executable control flow is present.

## State and Persistence Behavior
No state is modified. The comments indicate intended future coverage for trace-apply state and split progress persistence.

## Dependencies and Integration Points
None currently. Future tests would likely use the shared cluster split and failpoint helpers.

## Risks and Edge Cases
The absence of tests here means trace-apply split sequencing still relies on other failpoint and integration tests, especially `test_split.rs` and `tests/integrations/test_trace_apply.rs`.

## Test Signals
No direct test signals exist yet.
