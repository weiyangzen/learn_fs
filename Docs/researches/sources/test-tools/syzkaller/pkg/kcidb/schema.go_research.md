## sources/test-tools/syzkaller/pkg/kcidb/schema.go

Purpose: Go representation of KCIDB schema version 5.3 for checkouts, builds, tests, resources, issues, incidents, and misc fields.

Important APIs/types/functions: data structs `Kcidb`, `Build`, `BuildMisc`, `Environment`, `Checkout`, `Test`, `TestNumber`, `TestMisc`, `Resource`, `Version`, `Issue`, `IssueCulprit`, and `Incident` with JSON tags and omitempty semantics.

Control flow: no executable control flow; structs are marshaled by `client.go`.

State and persistence: schema determines serialized JSON shape for REST/file persistence.

Dependencies and integration: consumed by `Client.convert`; external contract is KCIDB ingestion/validation.

Risks: schema drift against upstream KCIDB can cause rejected submissions. Required JSON fields are represented by non-pointer strings but can still be empty if conversion omits values.

Test signals: no direct tests; optional `kcidb-validate` is the main compatibility signal.
