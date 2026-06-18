# sources/test-tools/xfstests/tests/generic/397

## Purpose
Test accessing encrypted files and directories, both with and without the encryption key. Access with the encryption key is more of a sanity check and is not intended to fully test all the encrypted I/O paths; to do that you'd need to run all the xfstests with encryption enabled. Access without the encryption key, on the other hand, should result in some particular behaviors. It is registered as generic/397 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the preallocation/range operations, rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key). Topic focus: preallocation/range operations, rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_symlinks; _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, diff, find, ln, ls, md5sum, mkdir, rm, stat, touch.

Representative `xfs_io` operations: pwrite 0 4k; pwrite 0 33k; pwrite 0 1k.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: stat: cannot statx 'SCRATCH_MNT/edir/empty': No such file or directory; stat: cannot statx 'SCRATCH_MNT/edir/symlink': No such file or directory; 8; 1; Required key not available; SCRATCH_MNT/edir/newfile: Required key not available. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
