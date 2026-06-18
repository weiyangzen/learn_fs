# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStorage.java

Purpose: `OMStorage` models the OM `VERSION` file on top of common `Storage`. It records OM-specific identity fields: legacy OM UUID, HA node ID, and certificate serial ID, and resolves the OM metadata directory.

Important APIs and types: constructor initializes `Storage` for `NodeType.OM` under `OMConfigKeys.OZONE_OM_DB_DIRS`. Mutators include `setOmId`, `setOmNodeId`, `setOmCertSerialId`, `unsetOmCertSerialId`, and `validateOrPersistOmNodeId`. Accessors read the stored properties. `getNodeProperties()` supplies persisted properties and creates a UUID if needed. `getOmDbDir()` delegates to `ServerUtils.getDBPath`.

Control flow: identity fields cannot be changed after `StorageState.INITIALIZED` except cert serial handling. `validateOrPersistOmNodeId` requires initialized storage, compares the configured node ID to the VERSION file, and persists it when missing for older deployments.

State and persistence: fields are persisted in the VERSION file, not RocksDB. The node ID ties an OM process to its metadata directory and HA/Raft identity.

Dependencies and integration points: used during OM init/startup, upgrade layout version selection, SCM certificate handling, and OM DB location selection.

Risks: mismatched node IDs indicate potentially dangerous metadata reuse; the error text warns against manual VERSION edits and unsafe majority metadata removal. Tests must protect behavior for pre-existing VERSION files without nodeId.

Test signals: cover fresh init UUID generation, post-init mutation rejection for OM ID/node ID, cert serial persistence/unset, node ID mismatch failures, missing node ID migration, and fallback/required metadata directory resolution.
