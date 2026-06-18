# sources/user-network-fs/rclone/lib/version/version_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version_test.go -->
## sources/user-network-fs/rclone/lib/version/version_test.go

Purpose: tests timestamp version insertion, removal, and matching.

Important APIs and control flow: `TestVersionAdd` checks insertion before extensions, stacked versions, unusual extensions, extensionless names, dotfiles, and empty names. `TestVersionRemove` validates parsed times rounded to milliseconds, restoring original names, removing only the last version suffix, and leaving malformed versions unchanged. `TestVersionMatch` checks regex detection for normal names, versioned names, stacked versions, empty names, and syntactically matching impossible timestamps.

State, dependencies, and integration: tests use fixed `fstest.Time` values and package `version_test` to exercise only exported APIs.

Risks and test signals: good coverage of file-name edge cases. Tests document that `Match` is syntax-only, not semantic date validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version_test.go -->
