# sources/sync-backup/restic/internal/fs/stat_windows_test.go

Purpose: Windows tests for recall-on-data-access detection.

Important APIs: `TestRecallOnDataAccessRealFile`, `mockFileInfo`, `TestRecallOnDataAccessMockCloudFile`, and `TestRecallOnDataAccessMockRegularFile`.

Control flow and state: Tests a real local temp file and mocked `Win32FileAttributeData` values with recall and archive attributes.

Dependencies and integration: Validates `stat_windows.go` and external-package public API behavior.

Risks: Real cloud placeholder behavior is mocked rather than requiring OneDrive or similar services.

Test signals: Confirms Windows placeholder detection is based on the expected file attribute bit.
