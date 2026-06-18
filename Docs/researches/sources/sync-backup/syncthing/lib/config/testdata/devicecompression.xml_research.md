# sources/sync-backup/syncthing/lib/config/testdata/devicecompression.xml

## sources/sync-backup/syncthing/lib/config/testdata/devicecompression.xml

Purpose: XML fixture for legacy and current device compression text values.

Important data: Version 5 config with devices using `compression="true"`, `compression="metadata"`, and `compression="false"`.

Control flow and state: `Compression.UnmarshalText` maps true/metadata to metadata and false to never during XML load.

Dependencies and integration: Used by `TestDeviceCompression`.

Risks and test signals: Protects compatibility with pre-enum boolean compression settings.
