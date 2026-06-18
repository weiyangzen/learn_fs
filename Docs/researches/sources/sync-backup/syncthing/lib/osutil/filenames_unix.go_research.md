## sources/sync-backup/syncthing/lib/osutil/filenames_unix.go

Purpose: filename normalization helpers for non-Windows, non-Darwin Unix-like platforms.

Important APIs: `NormalizedFilename` converts to NFC; `NativeFilename` returns the input unchanged.

Control flow and state: stateless.

Dependencies and integration points: used by filesystem/protocol conversion paths on Linux/BSD and other Unix targets.

Risks: assumes native filesystems do not require decomposition or separator conversion.

Test signals: no direct tests in this subset.
