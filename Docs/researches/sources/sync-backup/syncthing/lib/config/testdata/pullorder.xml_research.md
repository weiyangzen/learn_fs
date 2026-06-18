# sources/sync-backup/syncthing/lib/config/testdata/pullorder.xml

## sources/sync-backup/syncthing/lib/config/testdata/pullorder.xml

Purpose: XML fixture for pull-order enum parsing and round-trip behavior.

Important data: Version 10 config with folders using default, explicit supported pull orders, and an unknown `whatever` value.

Control flow and state: `PullOrder.UnmarshalText` maps supported strings and falls back to random for unknown/empty values; writing emits canonical strings.

Dependencies and integration: Used by `TestPullOrder`.

Risks and test signals: Protects scheduling option compatibility and serialization stability.
