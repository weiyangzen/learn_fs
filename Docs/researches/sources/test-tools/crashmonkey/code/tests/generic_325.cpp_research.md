# sources/test-tools/crashmonkey/code/tests/generic_325.cpp

Purpose: xfstests generic/325 mmap/msync persistence test. It writes a 256 KiB file, modifies the first and last 4 KiB through a shared mapping, msyncs the surrounding ranges, and expects the mapped writes to persist.

Important APIs/types/functions: `Generic325`, `WriteData`, `mmap`, `memcpy`, `msync(MS_SYNC)`, `munmap`, `Checkpoint`, `md5sum`, and `DataTestResult`.

Control flow: setup builds `foo_backup` with the same write and mmap/msync sequence, then syncs. Run creates `foo`, writes 256 KiB, syncs, mmaps it, writes repeated text at offsets 0 and 258048, msyncs 0-64 KiB and 192-256 KiB, unmaps, and checkpoints. Check compares `foo` to `foo_backup` by md5.

State/persistence behavior: dirty mmap pages at both file edges must be durable after `msync`, including the final page range near EOF.

Dependencies/integration: POSIX mmap/msync behavior and external `md5sum`.

Risks/test signals: `msync` lengths are larger ranges than the 4 KiB writes, and one `munmap` error path uses odd pointer/length values. The final signal is checksum mismatch.
