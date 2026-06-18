# sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesstatic.xml

## sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesstatic.xml

Purpose: XML fixture for migration of legacy static device addresses.

Important data: Version 3 config with IPv4, IPv6, and host:port address forms lacking the modern `tcp://` scheme.

Control flow and state: Loading applies migrations that wrap non-dynamic legacy addresses with TCP URLs while preserving explicit ports and IPv6 bracket forms.

Dependencies and integration: Used by `TestDeviceAddressesStatic`.

Risks and test signals: Ensures old address syntax still reaches the current dialer/listener URI format.
