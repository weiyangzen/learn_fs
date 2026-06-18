<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go

## Purpose
End-to-end directory operation suite for Blobfuse2 mounts, covering create, duplicate errors, special names, rename/move/delete, ADLS path-depth, stat/chmod/listing, Git workflow behavior, tar behavior, and symlinked directory reads.

## Important APIs, Types, and Functions
`dirTestSuite` stores mount test path, ADLS flag, cache path, and random buffers. Flag helpers configure mount path, temp path, ADLS, clone, stream-direct, and ADLS symlink support. Tests include `TestDirCreateSimple`, `TestDirCreateDuplicate`, `TestDirCreateSplChar`, `TestDirCreateSlashChar`, `TestDirRename`, `TestDirMoveEmpty`, `TestDirMoveNonEmpty`, `TestDirDeleteEmpty`, `TestDirDeleteNonEmpty`, `TestDirCreateDeepPath`, `TestDirGetStats`, `TestDirChmod`, `TestDirList`, `TestDirRenameFull`, `TestGitStash`, and `TestReadDirLink`.

## Control Flow and State
`TestDirTestSuite` creates a random top-level test directory on the mount, sets cache path, detects ADLS mode, fills buffers, runs the suite, and removes the test directory. Tests mutate the mounted tree and clean up per case. Some tests are conditional for ADLS, clone, stream-direct, or symlink support.

## Dependencies and Integration Points
Requires mounted Blobfuse2 path, temp cache path, optional network/git access for clone tests, `tar`, and `testify/suite`. ADLS-specific tests exercise hierarchical namespace semantics and permissions.

## Risks and Edge Cases
`TestGitStash` changes process working directory and performs a network clone, making it slow/flaky unless explicitly enabled. Stream-direct skips full-directory rename. ADLS symlink tests are gated. Some sleep calls compensate for eventual consistency/timing. Cleanup assumes generated paths are safe.

## Test Signals
Passing tests indicate POSIX-like directory semantics, expected errors for duplicates/non-empty deletes/deep ADLS paths, listing correctness, chmod on ADLS, and symlink directory traversal behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go -->
