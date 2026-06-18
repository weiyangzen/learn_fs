# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_unaligned.cpp

Purpose: unaligned plain fallocate variant. It checks that allocation of an unaligned in-file range does not expose stale data or zero data over the already written `0xff` content.

Important APIs/types/functions: `Generic042FallocateUnaligned`, `Generic042Base(65 KiB, 60 KiB + 128, 4 KiB, 0)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: inherited setup fills/frees the filesystem, inherited run writes 65 KiB, fallocates the unaligned range, fsyncs, and checkpoints. `check_test()` requires a complete recovered file to contain only `0xff` over the full written size.

State/persistence behavior: fallocate should be a metadata allocation operation here; it must not rewrite user-visible data bytes.

Dependencies/integration: generic/042 framework and Linux fallocate.

Risks/test signals: only content/size are checked, not extent layout. A failure indicates partial file recovery or data mismatch in the full range.
