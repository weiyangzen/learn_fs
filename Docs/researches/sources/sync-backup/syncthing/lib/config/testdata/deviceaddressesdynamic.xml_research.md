# sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesdynamic.xml

## sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesdynamic.xml

Purpose: XML fixture for dynamic/empty device address normalization.

Important data: Version 10 config with three devices: one with an empty `<address>`, one with no address elements, and one with explicit `dynamic`.

Control flow and state: When loaded, `DeviceConfiguration.prepare` converts empty or missing addresses to `[]string{"dynamic"}` and `Configuration.ensureMyDevice` can add the local device if absent.

Dependencies and integration: Used by `TestDeviceAddressesDynamic`.

Risks and test signals: Protects backward compatibility for legacy configs where empty address entries meant dynamic discovery.
