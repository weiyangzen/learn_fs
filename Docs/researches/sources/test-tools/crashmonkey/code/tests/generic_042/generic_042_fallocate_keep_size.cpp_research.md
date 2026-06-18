# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_fallocate_keep_size.cpp

Purpose: aligned `FALLOC_FL_KEEP_SIZE` allocation variant. It ensures keep-size allocation does not alter existing data bytes in the written file.

Important APIs/types/functions: `Generic042FallocateKeepSize`, `Generic042Base(64 KiB, 60 KiB, 4 KiB, FALLOC_FL_KEEP_SIZE)`, `CheckBase`, and `CheckDataNoZeros`.

Control flow: inherited setup/run create the stale-data environment, write 64 KiB of `0xff`, call keep-size fallocate in the final 4 KiB, fsync, and checkpoint. `check_test()` validates base size state and the full file data.

State/persistence behavior: since the fallocate range is inside the existing file, logical size remains 64 KiB and every byte should still be `0xff`.

Dependencies/integration: relies on Linux fallocate keep-size semantics and base helper validation.

Risks/test signals: this is not checking unwritten extent exposure outside EOF; it is an in-file no-data-change oracle. Any zero/stale mismatch is reported through base data corruption diagnostics.
