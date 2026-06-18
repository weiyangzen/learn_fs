# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fzero_keep_size_unaligned.cpp

Purpose: unaligned keep-size zero-range variant. It targets partial-block zeroing behavior with crash recovery.

Important APIs/types/functions: `Generic042FzeroKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_ZERO_RANGE | FALLOC_FL_KEEP_SIZE)`, `CheckBase`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base setup/run write 65 KiB, zero an unaligned 4 KiB range with keep-size, fsync, and checkpoint. The check validates size, nonzero prefix, zeroed range, and nonzero suffix.

State/persistence behavior: the zero range must be persisted exactly, and keep-size must preserve logical length despite unaligned extent boundaries.

Dependencies/integration: generic/042 base, Linux fallocate flags, and CrashMonkey's checkpoint harness.

Risks/test signals: sensitive to filesystem support for unaligned zero-range. The oracle reports stale leaked bytes, over-zeroed surrounding data, or partial-size files.
