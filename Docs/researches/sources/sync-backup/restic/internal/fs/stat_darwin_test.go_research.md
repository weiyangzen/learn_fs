# sources/sync-backup/restic/internal/fs/stat_darwin_test.go

Purpose: macOS tests for recall-on-data-access detection.

Important APIs: `TestRecallOnDataAccessRealFile`, `mockFileInfo`, `TestRecallOnDataAccessMockCloudFile`, `TestRecallOnDataAccessMockRegularFile`, and `TestRecallOnDataAccessMockError`.

Control flow and state: Tests real temp-file stat conversion and mock `os.FileInfo` values with `SF_DATALESS` set/unset. Error test constructs an `ExtendedFileInfo` without a Darwin sys payload.

Dependencies and integration: Validates `stat_darwin.go` and public `fs.ExtendedStat` from external package perspective.

Risks: Real file test only checks a normal local file; cloud state is simulated through mocks.

Test signals: Confirms correct detection and error reporting for macOS cloud placeholders.
