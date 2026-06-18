# sources/sync-backup/syncthing/lib/config/testdata/dupdevices.xml

## sources/sync-backup/syncthing/lib/config/testdata/dupdevices.xml

Purpose: XML fixture for duplicate device and duplicate folder-device pruning.

Important data: Version 12 config repeats a device at the root and repeats that device inside folder `f2`.

Control flow and state: `prepareDeviceList` removes duplicate root devices and `ensureNoDuplicateFolderDevices` removes duplicate folder shares before sorting.

Dependencies and integration: Used by `TestDuplicateDevices`.

Risks and test signals: Confirms duplicate device entries are repaired silently while duplicate folders remain fatal.
