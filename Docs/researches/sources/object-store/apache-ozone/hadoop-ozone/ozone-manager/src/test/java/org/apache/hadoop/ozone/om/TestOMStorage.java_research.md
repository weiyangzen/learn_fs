# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMStorage.java

Purpose: Tests OM storage directory resolution and VERSION-file-backed OM identity fields.

Important APIs and types: `OMStorage`, `OMStorage.getOmDbDir`, `setOmId`, `setOmNodeId`, `validateOrPersistOmNodeId`, `setOmCertSerialId`, `unsetOmCertSerialId`, `getNodeProperties`, storage state `INITIALIZED`, `OMLayoutVersionManager`, `OZONE_OM_DB_DIRS`, and `OZONE_METADATA_DIRS`.

Control flow: directory tests set OM DB and metadata dirs and verify primary/fallback behavior and missing-config failure. Identity tests create `OMStorage` before or after persisted initialization, attempt setters, persist current state, reload storage, and validate node ID rules. Certificate serial tests run both before and after initialization.

State and persistence: the test writes and reloads OM VERSION state in the temp OM DB dir. Persisted properties include cluster ID, layout version, OM ID, OM node ID, and cert serial ID.

Dependencies and integration points: storage initialization is a prerequisite for OM startup, HA node identity validation, upgrade layout versioning, and certificate tracking. Directory resolution integrates HDDS and OM-specific metadata config.

Risks and edge cases: `OM_ID` and `OM_NODE_ID` are immutable after initialization except `validateOrPersistOmNodeId` may fill a missing node ID; mismatched node IDs must fail with the formatted error; cert serial ID intentionally remains mutable. Directory fallback can accidentally create the wrong path if config precedence regresses.

Test signals: exact directory existence checks, exact error messages for initialized setters and unexpected node ID, properties map contents, reload persistence of newly written node ID, and null cert serial after unset.
