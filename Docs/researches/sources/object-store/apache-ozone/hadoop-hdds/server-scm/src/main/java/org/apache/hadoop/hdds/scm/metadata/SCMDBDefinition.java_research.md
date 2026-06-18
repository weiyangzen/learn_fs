# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBDefinition.java

Purpose: Authoritative RocksDB schema definition for SCM metadata database `scm.db`.

Important APIs and types: Defines column families for `deletedBlocks`, `validCerts`, `validSCMCerts`, `pipelines`, `containers`, `scmTransactionInfos`, `sequenceId`, `move`, `meta`, and `statefulServiceConfig`. Singleton `get` returns the definition; `getName` returns `scm.db`; `getLocationConfigKey` returns `OZONE_SCM_DB_DIRS`.

Control flow: Static column-family definitions pair table names with key/value codecs, then build an unmodifiable map consumed by `DBStoreBuilder`.

State and persistence behavior: Defines all persistent SCM RocksDB column families and their key/value encodings, including transaction info for HA snapshots and stateful service config bytes.

Dependencies and integration points: Used by `SCMMetadataStoreImpl`, checkpoint transaction-info reading in `SCMHAManagerImpl`, and any DB tooling that opens SCM metadata.

Risks and test signals: Changing names/codecs is upgrade-sensitive. Tests should assert all expected column families exist, codecs round-trip values, DB location key is stable, and checkpoint readers can locate transaction info.
