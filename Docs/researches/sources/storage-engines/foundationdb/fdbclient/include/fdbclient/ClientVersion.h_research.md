# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientVersion.h

Purpose: Provides `ClientVersionRef`, the lightweight serialized representation of a client binary version, source version, and protocol version reported to cluster coordination/open-database paths.

Important APIs/types/functions: `ClientVersionRef` stores three `StringRef` fields: `clientVersion`, `sourceVersion`, and `protocolVersion`. Constructors support unknown initialization, arena-deep-copy, direct three-part construction, and parsing a comma-separated version string. `serialize()` writes the three fields. `expectedSize()` reports aggregate string size. `operator<` sorts primarily by protocol version, then client version, then source version.

Control flow: Open-database and coordination request producers encode supported versions as `ClientVersionRef` values. String parsing accepts exactly three comma-separated parts; otherwise all fields become `"Unknown"`. Ordering is used for maps/sets that summarize client populations by version.

State and persistence behavior: The type is arena-backed when copied through the arena constructor and otherwise references external string memory via `StringRef`. There is no validation beyond the three-part split, and unknown initialization is the fallback persistence/display state.

Dependencies and integration points: Depends only on `flow/Arena.h` and Flow string utilities. Used by `ClusterInterface::OpenDatabaseRequest::supportedVersions` and `CoordinationInterface::OpenDatabaseCoordRequest::supportedVersions` to report client compatibility.

Risks: A malformed version string silently collapses all fields to unknown, reducing diagnostics. Because fields are `StringRef`, callers must ensure referenced memory outlives the object unless copied into an arena. Ordering is explicitly arbitrary except for protocol version, so it should not be interpreted as semantic release ordering.

Test signals: Parse tests for valid and invalid comma-separated strings; arena copy lifetime tests; map ordering/grouping by protocol; open-database client info aggregation with unknown and mixed versions.
