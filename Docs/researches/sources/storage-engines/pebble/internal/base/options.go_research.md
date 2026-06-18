# sources/storage-engines/pebble/internal/base/options.go

Purpose: Defines shared option interfaces for table filter policies and block property filters.

APIs and types: `TableFilterFamily`, `TableFilterWriter`, `TableFilterPolicy`, `TableFilterDecoder`, `NoFilterPolicy`, internal `noFilter`, and `BlockPropertyFilter`.

Control flow and state: Filter policies create writers/decoders for table filters. `NoFilterPolicy` names the disabled policy and panics for unsupported writer/decoder creation because it should not be used to build filters.

Persistence and dependencies: Filter names and serialized filter data are persisted in table metadata/blocks by implementations outside this file. Depends on CockroachDB errors for assertion panics.

Integration points: SSTable writers/readers, options parsing, and block-property filtering plug into these interfaces.

Risks: Interface implementations must keep names stable for compatibility. Accidentally invoking `NoFilterPolicy.NewWriter` is a programmer error and panics.

Test signals: No direct tests here; concrete filter policies and table readers/writers test implementations.
