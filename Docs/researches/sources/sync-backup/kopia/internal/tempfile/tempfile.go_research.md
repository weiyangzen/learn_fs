<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile.go

- Purpose: Documents the cross-platform tempfile package for private read-write files that auto-delete on close.
- Important APIs/types/functions: package declaration only.
- Control flow: Implementation is selected by platform-specific files in the same package.
- State and persistence: Actual state is OS file descriptors and temporary directory entries managed by platform implementations.
- Dependencies and integration points: No imports in this file.
- Risks and edge cases: Behavior depends entirely on platform-specific files and build tags.
- Test signals: `tempfile_test.go`, `tempfile_verify_test.go`, and Linux fallback tests cover behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile.go -->
