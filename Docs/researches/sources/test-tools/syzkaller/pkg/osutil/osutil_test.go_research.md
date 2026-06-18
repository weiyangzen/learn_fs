# sources/test-tools/syzkaller/pkg/osutil/osutil_test.go

Purpose: Tests broad `osutil` helper behavior for existence checks, copy/link pattern expansion, monotonic time, JSON helpers, Linux disk usage, and verbose error formatting.

Important tests: `TestIsExist`, `TestCopyFiles`, `TestMonotonicNano`, `TestReadWriteJSON`, `TestDiskUsage`, and `TestVerboseMessage`.

Control flow and state: `TestCopyFiles` table-drives required/optional glob patterns across both `CopyFiles` and `LinkFiles`, removes the source tree, and verifies destination existence. `TestDiskUsage` incrementally creates dirs/files/symlinks and asserts usage increases within ranges, skipping non-Linux. `TestVerboseMessage` checks wrapped `VerboseError` output inclusion.

Dependencies and integration: Covers core helpers used throughout syzkaller manager and test code.

Risks: Disk usage expected ranges are filesystem-dependent and only run on Linux. Copy/link tests verify existence but not file contents, permissions, or atomicity.

Test signals: Good utility-level regression coverage for common filesystem and error-message contracts.
