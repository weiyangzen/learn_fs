# sources/sync-backup/syncthing/lib/config/testdata/ignoredfolders.xml

## sources/sync-backup/syncthing/lib/config/testdata/ignoredfolders.xml

Purpose: XML fixture for per-device ignored folder pruning.

Important data: Version 28 config includes devices with ignored folders and a configured folder shared with one of those devices.

Control flow and state: Device preparation removes ignored-folder entries for folders now shared with that device and removes ignored folders for unavailable devices.

Dependencies and integration: Used by `TestIgnoredFolders`.

Risks and test signals: Ensures accepting or configuring a folder clears stale ignored state for the relevant device while preserving unrelated ignored folders.
