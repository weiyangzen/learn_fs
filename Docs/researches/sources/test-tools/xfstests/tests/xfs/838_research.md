<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/838 -->
# sources/test-tools/xfstests/tests/xfs/838

Purpose: validates multi-fsblock realtime atomic write support, including advertised size bounds, direct I/O requirements, and unaligned direct I/O rejection.

Important APIs, types, and functions: uses `statx -r -m $STATX_WRITE_ATOMIC`, `_get_atomic_write_unit_min/max`, `_simple_atomic_write`, `_test_atomic_file_writes`, realtime forcing, and xfs_io fallocate/fsync.

Control flow: query rt device atomic properties, mkfs/mount scratch, force realtime allocation, query file atomic properties, preallocate space, test sizes below and above advertised bounds, test every supported power-of-two size, then check buffered and unaligned direct I/O failures.

State and persistence behavior: writes to one scratch realtime file and logs statx data to `$seqres.full`.

Dependencies and integration points: depends on realtime, scratch atomic multi-fsblock support, atomicwrites common helpers, and xfs_io statx.

Risks and test signals: device capability discovery controls skips. Signals are expected EINVAL/EOPNOTSUPP lines and silent success for supported sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/838 -->
