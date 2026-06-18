# sources/test-tools/xfstests/tests/generic/399

## Purpose
Check for weaknesses in filesystem encryption involving the same ciphertext being repeated. For file contents, we fill a small filesystem with large files of 0's and verify the filesystem is incompressible. For filenames, we create an identical symlink in two different directories and verify the ciphertext filenames and symlink targets are different. This test can detect some basic cryptographic mistakes such as nonce reuse (across files), initialization vector reuse (across blocks), or data somehow being left in plaintext by accident. For example, it detects the initialization vector reuse bug fixed in commit 02fc59a0d28f ("f2fs/crypto: fix xts_tweak initialization"). It is registered as generic/399 with `_begin_fstest` tags `auto, encrypt`, making it part of the preallocation/range operations, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include fs_size_in_mb=64, fs_size=$((fs_size_in_mb * 1024 * 1024)), keydesc=$(_generate_session_encryption_key), total_file_size=0, i=1, fs_compressed_size=$(head -c $fs_size $SCRATCH_DEV | \, link1=$(find $SCRATCH_MNT/encrypted_dir -type l ..., link2=$(find $SCRATCH_MNT/encrypted_dir -type l .... Topic focus: preallocation/range operations, rename/link persistence. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_symlinks; _require_command "$XZ_PROG" xz; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, dd, find, grep, ln, mkdir.

Representative `xfs_io` operations: pwrite 0 1M.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: PASS: ciphertexts were not repeated for contents; 2. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
