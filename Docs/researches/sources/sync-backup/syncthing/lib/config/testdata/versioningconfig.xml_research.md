# sources/sync-backup/syncthing/lib/config/testdata/versioningconfig.xml

## sources/sync-backup/syncthing/lib/config/testdata/versioningconfig.xml

Purpose: XML fixture for versioning parameter parsing.

Important data: Version 22 config with folder `test`, versioning type `simple`, and two `<param>` entries.

Control flow and state: `VersioningConfiguration.UnmarshalXML` decodes internal param slices into a map; config preparation/migration preserves the parameters.

Dependencies and integration: Used by `TestVersioningConfig`.

Risks and test signals: Protects XML map encoding/decoding for versioner configuration.
