# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size.cpp

Purpose: aligned punch-hole keep-size variant of generic/042. It verifies that a punched 4 KiB region becomes zero while surrounding file data remains `0xff`.

Important APIs/types/functions: `Generic042FpunchKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base run writes 64 KiB, punches 4 KiB at offset 60 KiB, fsyncs, and checkpoints. `check_test()` validates the base state, checks bytes before the punched range for `0xff`, checks the punched range for zeros, then checks remaining bytes after the range.

State/persistence behavior: file size remains 64 KiB, but the hole reads as zeros. No stale pre-fill data should leak in the punched range.

Dependencies/integration: Linux hole punching semantics and base read/hexdump diagnostics.

Risks/test signals: catches both lost punch operations and over-broad zeroing of adjacent data.
