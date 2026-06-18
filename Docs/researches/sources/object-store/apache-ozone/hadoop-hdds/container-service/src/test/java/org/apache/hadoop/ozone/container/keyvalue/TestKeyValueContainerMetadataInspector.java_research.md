# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueContainerMetadataInspector.java

Purpose: verifies `KeyValueContainerMetadataInspector` activation, read-only/repair modes, JSON report content, and DB counter repair for block count, bytes used, and pending-delete block counts.

Important APIs/types/functions: extends `TestKeyValueContainerIntegrityChecks`; uses `KeyValueContainerMetadataInspector.SYSTEM_PROPERTY`, `Mode.INSPECT`, `Mode.REPAIR`, `ContainerInspectorUtil.load/unload`, `KeyValueContainerUtil.parseKVContainerData`, `BlockUtils.getDB`, schema two/three delete transaction tables, and nested `DeletedBlocksTransactionGeneratorForTesting`.

Control flow: activation tests clear/set the system property and assert inspector load/read-only behavior. Correct-container tests create containers with matching DB counters and assert no report in inspect or repair mode. Incorrect-total tests mutate DB metadata counts and run `inspectThenRepairOnIncorrectContainer()`, which captures JSON in inspect mode, validates errors without mutation, runs repair mode, validates `repaired=true`, then verifies DB metadata was corrected. Delete-count tests compare pending-delete count keys against the number of local IDs in delete transaction tables for schema 2 and schema 3 store implementations.

State and persistence behavior: tests directly mutate RocksDB metadata table values for block count, bytes used, pending delete count, and delete transaction rows. Inspector output is captured from its report logger as raw JSON. Repair mode writes corrected metadata values back to DB; inspect mode must not mutate DB. Container state and chunks directory file count are included in reports.

Dependencies and integration points: integrates container parsing, inspector plugin loading, log4j capture, Jackson JSON validation, schema-specific datanode store transaction tables, and inherited real container/chunk fixture generation.

Risks and test signals: strong signal for operational repair safety: disabled by default, inspect is read-only, repair is explicit. Exact JSON field assertions protect report contract but can be brittle for schema changes. The tests depend on global system properties and inspector load state, so cleanup is important.
