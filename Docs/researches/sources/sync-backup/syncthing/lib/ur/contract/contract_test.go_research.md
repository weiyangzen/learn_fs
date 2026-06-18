# sources/sync-backup/syncthing/lib/ur/contract/contract_test.go

Purpose: validates version-gated clearing and SQL scan reset behavior for usage-report contracts.

Important tests: fixture structs with nested structs, pointers, maps, slices, arrays, and `since` tags are passed through `clear` at versions 0 through 6. Expectations prove untagged fields are cleared, future fields are cleared, nested structs are recursively filtered, and pointer contents are handled. `TestMarshallingBehaviour` scans one JSON payload, then another, confirming the receiver is zeroed before unmarshal so old fields do not linger.

State and persistence: in-memory struct transformations only.

Dependencies and integration: targets the same reflection mechanism used by real `Report.ClearForVersion`.

Risks and signals: good coverage for version filtering, but does not validate the full `Report` field set, `Validate`, `Value`, or string scan inputs.
