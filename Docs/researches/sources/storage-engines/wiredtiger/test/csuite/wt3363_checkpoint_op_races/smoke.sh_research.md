# sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/smoke.sh

## Purpose
This smoke wrapper invokes the WT-3363 checkpoint-operation race executable in default and data-enabled modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Uses `$TEST_WRAPPER` to allow the harness to prefix execution.

## Control Flow
The script runs `./test_wt3363_checkpoint_op_races` and then `./test_wt3363_checkpoint_op_races -d`.

## State and Persistence Behavior
The script creates no state directly. The binary creates WiredTiger test homes and, unless timing tests are enabled, may exit immediately.

## Dependencies and Integration Points
It assumes execution from the directory containing the test binary. It is wired into make/ctest smoke flow.

## Risks and Test Signals
Because the binary is timing-gated, a smoke run can pass without running the 15-minute workload unless the environment flag is set. Any binary failure stops the script.
