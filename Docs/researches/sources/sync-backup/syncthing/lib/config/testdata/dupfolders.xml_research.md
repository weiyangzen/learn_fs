# sources/sync-backup/syncthing/lib/config/testdata/dupfolders.xml

## sources/sync-backup/syncthing/lib/config/testdata/dupfolders.xml

Purpose: XML fixture for rejecting duplicate folder IDs.

Important data: Version 15 config declares folder `f1` twice.

Control flow and state: `prepareFolders` detects the duplicate folder ID and returns an error containing `errFolderIDDuplicate`.

Dependencies and integration: Used by `TestDuplicateFolders`.

Risks and test signals: Duplicate folders are treated as dangerous because the GUI cannot safely resolve them; the test protects fail-fast behavior.
