# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_unaligned.cpp

Purpose: unaligned zero-range variant without keep-size. It stresses whether crash replay correctly records zeroing of a non-block-aligned in-file extent.

Important APIs/types/functions: `Generic042FzeroUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_ZERO_RANGE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: inherited code writes the file, performs the zero-range operation, fsyncs, checkpoints, and the derived checker verifies byte classes around the requested range.

State/persistence behavior: since the range lies inside the initial 65 KiB, size should remain complete and only the requested 4 KiB should become zeros.

Dependencies/integration: shared base class, Linux allocation APIs, and CrashMonkey plugin factory.

Risks/test signals: detects stale disk contents in zeroed ranges and unintended corruption in adjacent data.
