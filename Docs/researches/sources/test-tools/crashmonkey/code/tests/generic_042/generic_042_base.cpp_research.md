# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.cpp

Purpose: shared implementation for the generic/042 fallocate, punch-hole, and zero-range workloads. It creates a stale-data-sensitive environment, runs one parameterized fallocate operation, and provides reusable data-oracle helpers.

Important APIs/types/functions: `Generic042Base::setup`, `run`, `CheckBase`, `CheckDataNoZeros`, `CheckDataWithZeros`, `ReadData`, `HexdumpFile`, `WriteData`, `fallocate`, `fsync`, `Checkpoint`, and `DataTestResult`.

Control flow: `setup()` fills the filesystem by repeatedly writing 4 KiB chunks until `ENOSPC`, syncs, unlinks the filler file, syncs again, and creates an empty `foo`. `run()` writes `start_file_size_` bytes of `0xff`, applies `fallocate(fd, falloc_mode_, falloc_offset_, falloc_len_)`, fsyncs, checkpoints, and closes.

State/persistence behavior: recovered `foo` is allowed to be empty if the checkpoint did not fully replay, or full-sized with expected data once replay is complete. Derived classes decide whether the fallocated range should remain `0xff` or become zeros.

Dependencies/integration: integrates the base CrashMonkey lifecycle with Linux allocation flags and helper APIs from `user_tools/api/workload.h` and `actions.h`.

Risks/test signals: setup intentionally fills the filesystem, so capacity and ENOSPC behavior matter. `ReadData()` assumes reads make progress; unexpected short EOF behavior could loop. Failures include partial file size and stale data or missing zeros with hexdump diagnostics.
