# sources/storage-engines/pebble/internal/base/placement.go

Purpose: Defines object placement identifiers for local, shared, and external storage locations.

APIs and types: `Placement` enum values `Local`, `Shared`, and `External`, plus `String` and redact-safe formatting.

Control flow and state: `String` maps known enum values to stable labels. The zero value is intentionally invalid; unknown values panic when invariants are enabled and return `invalid` otherwise.

Persistence and dependencies: Placement identifiers describe where files/objects are stored and may be persisted by metadata in higher layers. Depends on `errors`, `invariants`, and `redact`.

Integration points: Used by object/table metadata and storage policy paths that distinguish local, shared, and external objects.

Risks: Callers must not rely on the zero value. Adding enum values requires updating string formatting and all metadata/storage consumers.

Test signals: No direct tests in this subset; behavior is simple.
