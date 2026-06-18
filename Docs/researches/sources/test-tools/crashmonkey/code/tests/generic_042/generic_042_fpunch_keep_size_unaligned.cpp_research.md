# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fpunch_keep_size_unaligned.cpp

Purpose: unaligned punch-hole keep-size variant. It stresses partial-block hole punching and recovery without permitting stale data leakage.

Important APIs/types/functions: `Generic042FpunchKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`, `CheckDataNoZeros`, and `CheckDataWithZeros`.

Control flow: base writes 65 KiB of `0xff`, punches an unaligned 4 KiB range, fsyncs, and checkpoints. The checker validates complete state, `0xff` before the range, zeros across the range, and `0xff` after it.

State/persistence behavior: hole punching should affect only the selected range. Unaligned offsets make this a stronger check for edge zeroing and stale extent replay.

Dependencies/integration: generic/042 base class, Linux fallocate punch flags, and CrashMonkey checkpointing.

Risks/test signals: range math is central; a wrong offset or length would make the oracle misleading. Failure appears as stale bytes in the hole or corrupted adjacent bytes.
