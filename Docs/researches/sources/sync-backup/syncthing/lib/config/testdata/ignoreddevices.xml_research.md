# sources/sync-backup/syncthing/lib/config/testdata/ignoreddevices.xml

## sources/sync-backup/syncthing/lib/config/testdata/ignoreddevices.xml

Purpose: XML fixture for root-level ignored remote device pruning.

Important data: Version 15 config includes two configured devices and two `remoteIgnoredDevice` entries, one of which matches a configured device.

Control flow and state: `prepareIgnoredDevices` removes ignored-device entries that are already present in `Devices` and keeps only unknown ignored devices.

Dependencies and integration: Used by `TestIgnoredDevices` and `TestGetDevice`.

Risks and test signals: Ensures manual device addition overrides prior ignored state.
