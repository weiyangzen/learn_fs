# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size_unaligned.cpp

Purpose: unaligned keep-size allocation variant of generic/042. It stresses allocation/recovery when the file size and fallocate offset are not block-aligned to the same 64 KiB boundary as the simpler case.

Important APIs/types/functions: `Generic042FallocateKeepSizeUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, FALLOC_FL_KEEP_SIZE)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: base run writes 65 KiB of `0xff`, applies keep-size fallocate at an offset 128 bytes past 60 KiB, fsyncs, and checkpoints. The checker validates complete base state and then verifies all 65 KiB remain nonzero `0xff`.

State/persistence behavior: unaligned allocation must not corrupt surrounding file data or truncate/extend the visible file beyond the written size.

Dependencies/integration: uses the generic/042 base and Linux fallocate flags.

Risks/test signals: useful for boundary bugs around partial blocks. Failure is any byte not equal to `0xff` or a partial-size recovered file.
