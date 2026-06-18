# sources/sync-backup/syncthing/lib/config/testdata/nopath.xml

## sources/sync-backup/syncthing/lib/config/testdata/nopath.xml

Purpose: XML fixture for rejecting folders without a path.

Important data: Version 15 config with folder `f1` and no `path` attribute.

Control flow and state: `prepareFolders` returns an error wrapping `errFolderPathEmpty`.

Dependencies and integration: Used by `TestEmptyFolderPaths`.

Risks and test signals: Prevents accidental normalization of an empty path into current directory or filesystem root.
