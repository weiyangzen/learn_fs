# sources/sync-backup/syncthing/lib/config/testdata/nolistenaddress.xml

## sources/sync-backup/syncthing/lib/config/testdata/nolistenaddress.xml

Purpose: XML fixture for preserving an explicit empty listen address.

Important data: Version 1 config with `<listenAddress></listenAddress>`.

Control flow and state: Loading keeps `RawListenAddresses` as `[]string{""}` rather than replacing it with default listen addresses.

Dependencies and integration: Used by `TestNoListenAddresses`.

Risks and test signals: Protects historical behavior for users who intentionally disabled listening through an empty entry.
