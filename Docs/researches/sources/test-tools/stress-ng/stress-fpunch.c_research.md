<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fpunch.c -->
# sources/test-tools/stress-ng/stress-fpunch.c Research

Purpose: implements `fpunch`, a filesystem/OS stressor that creates sparse files and has child processes repeatedly exercise `fallocate()` modes such as keep-size allocation, hole punching, zero range, collapse range, and insert range.

Important APIs/types/functions: `stress_fallocate_modes_t` describes each fallocate mode and whether pre/post writes or zero verification are required. `stress_punch_buf_t` holds write/read buffers. `stress_punch_pwrite()` abstracts `pwrite()` versus `lseek()+write()`. `stress_punch_check_zero()` verifies zeroed ranges. `stress_punch_action()` performs one operation and optional validation. `stress_punch_file()` loops across offsets and modes. `stress_fpunch()` handles temp file setup, sparse prepopulation, child orchestration, metrics, and cleanup.

Control flow: the top-level stressor clamps `fpunch-bytes`, divides work by instance count, maps a shared PID array and a private buffer, creates a temp directory/file, writes alternating data/hole extents backward, then forks four child workers. Children synchronize through `stress_sync_start_*`, install a SIGALRM exit handler, and call `stress_punch_file()` on the shared file descriptor or their own descriptor when `preadv/pwritev` support is absent. The parent releases children, sleeps for the configured timeout, kills/waits them, records extents per file, unlinks the file, and removes the temp directory.

State and persistence: the temporary file is unlinked during cleanup and the temporary directory is removed. PID synchronization state lives in an mmap allocated by stress-ng helpers. Static previous offset/size caching in `stress_punch_action()` is per process.

Dependencies and integration: requires `HAVE_FALLOCATE`; otherwise it registers as unimplemented. It uses stress-ng FS temp helpers, sync PID maps, kill/wait helpers, mmap/madvise, signal handling, and filesystem metrics.

Risks: fallocate mode support and alignment rules vary by filesystem, and many failures are intentionally ignored. Verification only checks zeroing for instance zero and selected offsets. Shared file descriptors can race on systems without positional I/O, so the code reopens per child in that case. Large defaults can consume real filesystem space depending on sparse-file behavior.

Test signals: bogo operations come from child fallocate loops; parent reports extents per file. Verify mode can report nonzero data after zero-range operations. Test across ext4/xfs/tmpfs and with constrained disk space.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fpunch.c -->
