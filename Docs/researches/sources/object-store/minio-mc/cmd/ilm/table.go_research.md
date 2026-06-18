# Research: sources/object-store/minio-mc/cmd/ilm/table.go

Purpose: defines table abstractions and row types for rendering lifecycle rules.

Important APIs/types/functions: `Table`, `LsFilter`, `LsFilter.Apply`, current/noncurrent expiration and transition table/row types, and their `Len`, `Title`, `Rows`, and `ColumnHeaders` methods.

Control flow: `LsFilter.Apply` filters lifecycle rules in place based on expiry or transition actions. Table row builders normalize empty prefix/tags to `-` and return `go-pretty` rows with stable headers.

State and persistence: pure display transformation; no persistence.

Dependencies/integration points: used by `ilm-rule-list.go` and `utils.go` `ToTables`.

Risks: `Apply` mutates the input slice contents and length, so callers should not expect original ordering plus excluded rules afterward. Table headers are user-facing and JSON-independent.

Test signals: `options_test.go` does not cover this; useful tests would verify filter behavior and row output for empty fields.
