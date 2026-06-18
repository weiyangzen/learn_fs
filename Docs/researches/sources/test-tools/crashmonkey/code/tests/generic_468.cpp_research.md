# sources/test-tools/crashmonkey/code/tests/generic_468.cpp

Purpose: EOF block allocation persistence test. It allocates blocks beyond EOF with keep-size after an initial fsync epoch and expects the increased block count to survive `fdatasync` and crash recovery.

Important APIs/types/functions: `EOFBlocksLoss`, `WriteData`, `syncfs`, `fsync`, `fallocate(FALLOC_FL_KEEP_SIZE)`, `fdatasync`, `Checkpoint`, `stat`, and `DataTestResult::kIncorrectBlockCount`.

Control flow: setup creates `test_file`, writes 8 KiB at offset 8 KiB, syncs, and closes. Run opens the file, fsyncs and checkpoints once, calls `syncfs` to force a separate epoch, keep-size fallocates 8 KiB at offset 4,202,496, calls `fdatasync`, checkpoints again, and closes.

State/persistence behavior: after checkpoint 2, logical size can remain 16 KiB but block count should increase beyond the original 16 blocks. If `st_blocks` remains 16, EOF allocation was lost.

Dependencies/integration: fixed mount path and Linux fallocate/fdatasync behavior.

Risks/test signals: expected block count baseline is filesystem-dependent. Signal is missing file or unchanged block count after checkpoint 2.
