# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero.cpp

Purpose: aligned zero-range variant. It verifies that `FALLOC_FL_ZERO_RANGE` zeros the selected in-file extent and leaves surrounding data unchanged after crash recovery.

Important APIs/types/functions: `Generic042Fzero`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_ZERO_RANGE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base run writes `0xff` data, zero-ranges the final 4 KiB, fsyncs, and checkpoints. `check_test()` accepts empty pre-replay state, otherwise checks nonzero prefix, zeroed range, and nonzero suffix.

State/persistence behavior: after checkpoint replay, the zero-range operation must be durable as zeros, not stale preexisting data or the original `0xff` bytes.

Dependencies/integration: generic/042 stale-block setup and Linux zero-range fallocate.

Risks/test signals: suffix length may be zero in the aligned final-range case; helpers still encode the expected byte classes. Failure is stale data leakage or incorrect zeroing.
