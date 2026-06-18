# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStoreImpl.java

Purpose: RocksDB-backed implementation of `SCMMetadataStore`, opening `scm.db`, initializing typed table handles, and exposing them to SCM managers.

Important APIs and types: Constructor calls `start`; `start` creates the DB store from `SCMDBDefinition`, checks the transient inconsistency marker, initializes all table fields, and populates `tableMap`. Getters expose deleted blocks, certificates, pipelines, containers, transaction info, sequence ids, move table, meta table, stateful service config, batch handler, and raw `DBStore`. `stop` closes the store.

Control flow: Startup is idempotent when `store` is non-null. It derives the metadata directory, terminates if `DB_TRANSIENT_MARKER` exists, opens the store with `DBStoreBuilder`, fetches each table from its column-family definition, and rejects null table references.

State and persistence behavior: Owns the live `DBStore`, typed table handles, and table map. The DB is durable RocksDB state under the configured SCM DB directory.

Dependencies and integration points: Used by nearly every SCM manager, HA checkpoint install/reload, sequence-id upgrades, and finalization.

Risks and test signals: Inconsistent-marker handling terminates the process. Reopen after `stop` depends on `store` nulling and existing table fields being replaced. Tests should cover table initialization, marker termination, stop/restart, null table failure, and all getter references matching `SCMDBDefinition`.
