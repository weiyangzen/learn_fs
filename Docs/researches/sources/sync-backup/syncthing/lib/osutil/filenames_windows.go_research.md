## sources/sync-backup/syncthing/lib/osutil/filenames_windows.go

Purpose: Windows filename normalization helpers.

Important APIs: `NormalizedFilename` converts path separators to slashes and normalizes Unicode to NFC; `NativeFilename` converts slashes to Windows separators.

Control flow and state: stateless path and Unicode conversions.

Dependencies and integration points: used when translating between protocol paths and native Windows paths. Important for request/symlink and encrypted metadata paths.

Risks: path separator conversion must not be applied to already-native strings in the wrong direction. Unicode normalization can interact with case-insensitive filesystem behavior.

Test signals: indirectly covered by Windows-specific model tests.
