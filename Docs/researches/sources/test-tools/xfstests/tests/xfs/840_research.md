<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/840 -->
# sources/test-tools/xfstests/tests/xfs/840

Purpose: hardware large atomic write error-injection test for reflinked files, validating shutdown and log replay behavior.

Important APIs, types, and functions: uses `_scratch_inject_error bmap_finish_one`, `_require_scratch_write_atomic`, xfs_io `pwrite -A -D -V1`, reflink copy, `_scratch_remount_dump_log`, and md5sum comparisons.

Control flow: mkfs/mount scratch, create two reflinked files, record checksums, inject bmap finishing error, attempt a 4 KiB atomic direct write to one file, confirm the filesystem shuts down, remount to replay the log, recheck checksums, and confirm the filesystem is usable.

State and persistence behavior: writes reflinked scratch data and exercises journal recovery across a forced shutdown.

Dependencies and integration points: depends on reflink, hardware atomic write support, xfs_io atomic pwrite, and inject helpers.

Risks and test signals: skips if 4 KiB atomic writes are unavailable. Signals are expected shutdown, stable checksums, and successful post-replay touch.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/840 -->
