<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/api.go -->
# sources/test-tools/syzkaller/dashboard/api/api.go research

Purpose: stable JSON data model for syzkaller dashboard export/API consumers.

Important APIs, types, and functions: declares `Version = 1` and DTO structs `BugGroup`, `BugSummary`, `Bug`, `Crash`, and `Commit` with JSON tags. The structs describe bug lists, individual bug metadata, crash reproduction/build links, and commit identity/repository fields.

Control flow: there are no functions in this file. The control contract is serialization compatibility: dashboard handlers populate these structs, and clients validate the `Version` field.

State and persistence: no state is stored here. `time.Time` and pointer time fields encode persisted dashboard timestamps when marshaled.

Dependencies and integration: imported by API clients and dashboard JSON endpoints; `client.go` reflects on the `Version` field after unmarshalling.

Risks: all structures are documented as backwards compatible, so removing/renaming fields or changing JSON tags breaks external consumers. Version remains coarse-grained, so additive changes must remain optional.

Test signals: JSON round trips, API client version checks, and consumers handling omitted optional fields are the main validation points.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/api.go -->
