# sources/sync-backup/kopia/tests/end_to_end_test/compression_test.go

## Purpose
Format-specific end-to-end test that global compression policy applies to uploaded file data and that content can still be shown correctly.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestCompression` and helper `containsLineStartingWith`.

## Control Flow
The test creates a repo, sets global compression to `pgzip`, writes a small compressible file, snapshots it, lists the directory to get the object ID, detects whether repository status reports content-level compression, then either checks object ID prefix or `content ls -c` compression metadata. Finally it runs `show` and compares the original lines.

## State and Persistence Behavior
Persists a global policy manifest, compressed content/object data, and one snapshot. Reads repository status and content metadata.

## Dependencies and Integration Points
Integrates policy CLI, upload compression policy, repository format differences, `ls`, `content ls`, and `show`.

## Risks
Output parsing depends on status and content-list text. The test is intentionally small and does not measure compression ratio.

## Test Signals
Confirms compression metadata/path differs correctly by format capability and decompression/show returns original content.
