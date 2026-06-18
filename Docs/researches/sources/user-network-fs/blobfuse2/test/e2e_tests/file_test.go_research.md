<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go

## Purpose
End-to-end file operation suite for Blobfuse2 mounts, covering create/open/truncate/read/write/stat/chmod/copy/delete, special and Unicode names, and symlink behavior.

## Important APIs, Types, and Functions
`fileTestSuite` stores mount path, ADLS mode, cache path, and buffers. Flag helpers configure mount, temp, ADLS, clone, stream-direct, distro, and ADLS symlink support. Tests cover basic creation, `O_TRUNC`, UTF-8 and special names, long names, backslash names, label-like names, small read/write, duplicate create, truncate, file/dir name conflict, copy, stat, chmod, multiple medium files, delete, symlink create/read/write/rename/delete, symlink listing/readlink, ADLS read-only creation, and special-character rename.

## Control Flow and State
`TestFileTestSuite` creates a random test directory under the mount, initializes buffers, detects ADLS mode, runs the suite, and removes the directory. Tests manipulate mounted files directly and clean up paths individually.

## Dependencies and Integration Points
Requires live Blobfuse2 mount and temp cache path. Uses Go standard `os`, `io`, `time`, `crypto/rand`, and `testify/suite`. ADLS-specific chmod/read-only/symlink behavior is conditionally tested.

## Risks and Edge Cases
Several tests depend on timing (`time.Sleep`) and mounted filesystem consistency. `TestFileCopy` appears to call `io.Copy(srcFile, dstFile)` from newly created destination to source, which exercises copy plumbing weakly because source/destination naming is counterintuitive. `TestLinkDeleteReadTarget` calls `os.Remove(symName)` twice before asserting only the second error path could matter. Stream-direct/distro gating can skip multi-file coverage.

## Test Signals
Passing tests show broad POSIX file compatibility over Blobfuse2, especially path encoding, symlink behavior, truncation, and metadata. Some individual tests are smoke-level rather than deep data-integrity checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go -->
