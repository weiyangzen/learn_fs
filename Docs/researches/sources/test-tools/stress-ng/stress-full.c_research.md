<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-full.c -->
# sources/test-tools/stress-ng/stress-full.c Research

Purpose: implements `full`, a device/memory/OS stressor that validates and exercises `/dev/full` behavior: writes fail with ENOSPC, reads return zeroes, and miscellaneous file operations behave consistently.

Important APIs/types/functions: `stress_full()` is the main stressor. Linux builds also define a `whences[]` table for rotating `lseek()` tests. `stress_full_info` registers VERIFY_ALWAYS or an unimplemented placeholder on unsupported platforms.

Control flow: the stressor maps a 4096-byte anonymous buffer, synchronizes, then repeatedly opens `/dev/full`. It writes and expects failure with `ENOSPC` except for transient `EAGAIN`/`EINTR`, reads and verifies the buffer is all zero, optionally tests `pread()` at a random offset, calls `fstat()`, tries read and write mappings plus `msync()`, rotates Linux `lseek()` calls over `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`, exercises `FIONREAD` and `FIGETBSZ` ioctls when present, closes the fd, and increments bogo operations.

State and persistence: only the anonymous buffer and current fd are held. No persistent state is written. The device path is opened fresh each iteration and closed before the next loop.

Dependencies and integration: uses stress-ng mmap/madvise, zero-data checking, put helpers, fstat shim, metrics-free bogo accounting, and state transitions. The platform guard permits Linux, Sun, FreeBSD, and NetBSD, although the unimplemented reason text says Linux only.

Risks: `/dev/full` may be absent in containers or nonstandard systems; ENOENT becomes `EXIT_NOT_IMPLEMENTED`. mmap behavior for `/dev/full` can vary and failures are tolerated. The platform guard and unimplemented reason are slightly inconsistent.

Test signals: healthy runs produce bogo progress only. Failure logs identify incorrect write errno, nonzero read data, read/pread/fstat/lseek failures, or open failure. Test with `/dev/full` missing, container device policies, and Linux ioctl availability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-full.c -->
