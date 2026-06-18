# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/ContainerTestVersionInfo.java

Purpose: defines the cross-product of container metadata schema versions and chunk layout versions used by many parameterized key-value container tests.

Important APIs/types/functions: `SCHEMA_VERSIONS` includes `null`, `SCHEMA_V1`, `SCHEMA_V2`, and `SCHEMA_V3`; static `layoutList`; constructor/getters; `toString()`; `getLayoutList()`; `setTestSchemaVersion(String,OzoneConfiguration)`; and composite `@ContainerTest` sourcing this class.

Control flow: the static initializer iterates all `ContainerLayoutVersion.getAllVersions()` and every schema entry, appending a `ContainerTestVersionInfo` for each pair. Tests annotated with `@ContainerTest` receive each pair. `setTestSchemaVersion()` enables schema V3 only when the requested schema matches V3; all other values disable schema V3.

State and persistence behavior: instances are immutable parameter values. The mutable state is the static list and the supplied `OzoneConfiguration`, which is toggled to choose schema V3 shared-DB behavior versus older per-container DB behavior.

Dependencies and integration points: integrates JUnit parameterization with Ozone schema toggles in `ContainerTestUtils` and schema comparison in `KeyValueContainerUtil`. It is used heavily by disk balancer, iterator, container, scanner, metadata-inspector, and reconciliation tests.

Risks and test signals: ensures broad compatibility coverage across layouts and schema versions, including default/null schema behavior. Adding a schema version or layout automatically multiplies test coverage, which is useful but can increase runtime or expose assumptions in older tests.
