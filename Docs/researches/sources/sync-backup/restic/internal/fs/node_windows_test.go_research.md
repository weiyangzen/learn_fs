# sources/sync-backup/restic/internal/fs/node_windows_test.go

Purpose: Windows-only integration tests for generic attributes, security descriptors, EAs, and volume path handling.

Important APIs: `TestRestoreSecurityDescriptors`, `TestRestoreSecurityDescriptorInheritance`, `TestRestoreSecurityDescriptorInheritanceLowPrivilege`, `TestRestoreCreationTime`, `TestRestoreFileAttributes`, `TestNewGenericAttributeType`, `TestRestoreExtendedAttributes`, `TestPrepareVolumeName`, and `TestGetVolumePathName`.

Control flow and state: Tests construct `data.Node` values with Windows generic attributes, restore metadata to temporary files/directories, reopen them through `NewLocal`, and compare serialized attributes. Volume tests cover drive paths, UNC/extended UNC, `GLOBALROOT`, volume GUID paths, relative/empty paths, and invalid paths.

Dependencies and integration: Exercises `node_windows.go`, `sd_windows.go`, `ea_windows.go`, and data generic-attribute conversions.

Risks: Some cases require admin privileges, system drive assumptions, encryption support, or real Windows path semantics. The tests are necessarily platform-integration heavy.

Test signals: Broadest Windows metadata coverage in this subset, including low-privilege inheritance behavior and unknown generic attribute warnings.
