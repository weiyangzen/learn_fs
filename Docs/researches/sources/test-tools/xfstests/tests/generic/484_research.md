# sources/test-tools/xfstests/tests/generic/484

## Purpose
Open a file and write to it and fsync. Then, flip the data device to throw errors, write to it again and do an fdatasync. Then open an O_RDONLY fd on the same file and call syncfs against it and ensure that an error is reported. Then call syncfs again and ensure that no error is reported. Finally, repeat the open and syncfs and ensure that there is no error reported. Kernel with the following patches should pass the test: vfs: track per-sb writeback errors and report them to syncfs buffer: record blockdev write errors in super_block that it backs. It is registered as generic/484 with `_begin_fstest` tags `auto, quick, eio`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testfile=$SCRATCH_MNT/syncfs-reports-errors, datalen=$(getconf PAGE_SIZE). Topic focus: writeback error reporting. Key helper behavior includes: formats a fresh scratch filesystem; sets up dm-error for I/O fault injection.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_dm_target error; _require_xfs_io_command "syncfs".

External/helper commands: $XFS_IO_PROG, mount, rm, touch.

Representative `xfs_io` operations: pwrite -W -q 0 $datalen; pwrite -w -q 0 $datalen.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; fdatasync: Input/output error; One of the following syncfs calls should fail with EIO:; syncfs: Input/output error; done; This syncfs call should succeed:. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
