# sources/test-tools/xfstests/tests/generic/761


Purpose: Verifies that direct writes cannot race mutable user buffers into bad data checksums; checksum filesystems should fall back to buffered writes when required.


Important APIs, helpers, and commands: Requires `dio-writeback-race`, scratch, and O_DIRECT; uses `_get_file_block_size` and a 64MiB target file.
 It imports `./common/preamble`.
 Capability gates include `_require_odirect`, `_require_scratch`, `_require_test_program`.
 Regression annotations include `_fixed_by_fs_commit btrfs 968f19c5b1b7 \`.



Control flow, state, dependencies, risks, and test signals: The test mkfs/mounts scratch, records block size and file size, runs the helper to mutate a direct-I/O buffer during writeback, then reads the file to force checksum verification. State is file data and filesystem checksum metadata. Dependencies are the compiled helper and checksum-capable behavior on affected filesystems. Risks are helper timing sensitivity and filesystems without data checksums simply not exercising the bug. Signal is helper or read failure; otherwise silence. Source size is 42 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
