# sources/sync-backup/syncthing/lib/config/testdata/example.xml

## sources/sync-backup/syncthing/lib/config/testdata/example.xml

Purpose: Representative legacy config fixture used for migration, copy, and save/load tests.

Important data: Version 10 config with a default folder, three devices, GUI settings, and old options such as UDP discovery servers, old local announce port/group, UPnP fields, old listen address syntax, read-only flag, and puller count.

Control flow and state: Loading migrates addresses, discovery, local announce settings, NAT fields, folder type, puller settings, defaults, and current version. Save/load tests persist the prepared config back to XML and reload it.

Dependencies and integration: Used by `TestCopy`, `TestNewSaveLoad`, the skipped device-removal share test, and historical migration coverage.

Risks and test signals: Provides broad compatibility coverage for realistic old configuration state and deep-copy isolation.
