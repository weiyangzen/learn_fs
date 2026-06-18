# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size.cpp

Purpose: aligned zero-range keep-size variant. It checks that keep-size zeroing of an in-file range persists zeros without changing logical file size.

Important APIs/types/functions: `Generic042FzeroKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: the inherited workload writes 64 KiB, zero-ranges the last 4 KiB with keep-size, fsyncs, and checkpoints. The checker validates complete file state and byte classes around the zeroed range.

State/persistence behavior: file size should remain at `start_file_size_`, the selected range should read zeros, and nonselected bytes should remain `0xff`.

Dependencies/integration: shared generic/042 base and Linux fallocate semantics.

Risks/test signals: this is the generic counterpart to keep-size EOF bugs; it catches both missing zeroing and accidental size/data corruption.
