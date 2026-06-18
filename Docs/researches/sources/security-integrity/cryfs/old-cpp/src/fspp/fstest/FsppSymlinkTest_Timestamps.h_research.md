# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest_Timestamps.h

Purpose: timestamp tests for reading a symlink target under different atime policies.

Important APIs/types/functions: `FsppSymlinkTest_Timestamps`, `Symlink::target`, `setAtimeNewerThanMtimeButBeforeYesterday`, `setAtimeOlderThanMtime`, `setAtimeNewerThanMtime`, and timestamp expectation helpers.

Control flow: each test creates a symlink, forces a specific atime/mtime relationship, captures a closure that calls `target()`, then runs expectations across noatime, strictatime, relatime, nodiratime+relatime, and nodiratime+strictatime contexts.

State and persistence behavior: metadata is mutated by `utimens` in setup and then compared around target reads. Since symlinks are not directories, nodiratime modes behave like their corresponding file/symlink atime modes.

Dependencies and integration points: inherits from `TimestampTestUtils`; integrates with `FileSystemTest::CreateSymlink` and fspp context updates.

Risks and test signals: covers relatime edge cases for symlink target reads. It does not test symlink creation timestamps directly or failure modes for missing/corrupt symlink target metadata.
