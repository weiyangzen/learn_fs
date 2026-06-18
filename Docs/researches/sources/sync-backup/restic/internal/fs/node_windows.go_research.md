# sources/sync-backup/restic/internal/fs/node_windows.go

Purpose: Windows-specific node metadata, extended attributes, generic attributes, encryption flags, security descriptors, and volume handling.

Important APIs: `mknod`, `lchown`, `utimesNano`, `nodeRestoreExtendedAttributes`, `nodeFillExtendedAttributes`, `restoreExtendedAttributes`, `nodeRestoreGenericAttributes`, `genericAttributesToWindowsAttrs`, `restoreCreationTime`, `restoreFileAttributes`, `fixEncryptionAttribute`, `nodeFillGenericAttributes`, `checkAndStoreEASupport`, `getVolumePathName`, `isVolumePath`, and `prepareVolumeName`.

Control flow and state: Timestamp restore opens paths with backup semantics and open-reparse-point. EA backup skips alternate data streams and non-file/dir nodes, checks per-volume EA support with a `sync.Map`, opens EA handles, and reads/writes all EAs at once. Generic attributes serialize creation time, file attributes, and security descriptors; restore parses them and applies creation time, attributes, and SDs. Encryption toggles call `EncryptFileW`/`DecryptFileW`, temporarily resetting permissions/system flags on access errors.

Dependencies and integration: Uses `data.WindowsAttributes`, `sd_windows.go`, `ea_windows.go`, `file_windows.go`, Windows syscalls, and restic error/debug helpers. This is the main Windows metadata fidelity layer for backup/restore.

Risks: High-risk code due to unsafe syscalls, path normalization, alternate data stream exclusions, case-insensitive EAs, privilege-dependent SD handling, and mutable global EA support cache. Fallbacks can silently skip unsupported volumes.

Test signals: `node_windows_test.go`, `ea_windows_test.go`, `sd_windows_test.go`, and xattr tests cover SD restore, inheritance flags, creation time, file attributes including encryption, EAs, volume-name parsing, and EA support checks.
