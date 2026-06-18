# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMConfigurator.java

Purpose: `SCMConfigurator` is a test and extension builder object for injecting custom SCM manager implementations into `StorageContainerManager` construction. It lets tests replace selected managers without rewriting the full SCM startup path.

Important APIs and types: It has setters and getters for `NodeManager`, `PipelineManager`, `ContainerManager`, `BlockManager`, `ReplicationManager`, `SCMSafeModeManager`, `CertificateServer`, `SCMMetadataStore`, `NetworkTopology`, `SCMHAManager`, `SCMContext`, `WritableContainerFactory`, upgrade finalization executor, and `LeaseManager<Object>`.

Control flow: The class is a passive holder. SCM construction code reads configured values and uses defaults for null values. There is no validation, ordering, or lifecycle management here.

State and persistence behavior: State is only in-memory object references. It does not persist configuration and does not own injected managers.

Dependencies and integration points: It touches most major SCM subsystems and is important for unit/integration tests that need mocked managers, custom metadata stores, or specialized finalization behavior.

Risks: Because all fields are optional and unvalidated, inconsistent combinations can fail later in SCM startup. The class is mutable and not thread-safe; it should be treated as construction-time only.

Test signals: Tests should verify default-manager fallback in SCM construction, successful use of each injected manager, and failures for incompatible injected combinations where appropriate.
