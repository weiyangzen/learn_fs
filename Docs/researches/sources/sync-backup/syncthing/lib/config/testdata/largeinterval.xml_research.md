# sources/sync-backup/syncthing/lib/config/testdata/largeinterval.xml

## sources/sync-backup/syncthing/lib/config/testdata/largeinterval.xml

Purpose: XML fixture for clamping invalid folder rescan intervals.

Important data: Version 10 config has one overly large `rescanIntervalS` and one negative interval.

Control flow and state: `FolderConfiguration.prepare` clamps values above `MaxRescanIntervalS` down to the maximum and negative values to zero.

Dependencies and integration: Used by `TestLargeRescanInterval`.

Risks and test signals: Prevents pathological scan intervals from persisting into scheduler behavior.
