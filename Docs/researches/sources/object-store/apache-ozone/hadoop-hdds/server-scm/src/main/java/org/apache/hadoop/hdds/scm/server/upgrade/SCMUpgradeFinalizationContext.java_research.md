# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizationContext.java

Purpose: This immutable context object supplies SCM-specific dependencies to upgrade finalization code. It packages the managers and storage/configuration objects needed by `SCMUpgradeFinalizer` and layout-feature actions.

Important APIs and types: The context exposes getters for `NodeManager`, `PipelineManager`, `FinalizationStateManager`, `OzoneConfiguration`, `HDDSLayoutVersionManager`, `SCMContext`, and `SCMStorageConfig`. The nested builder has setters for each required field and validates all fields in `build`.

Control flow: `FinalizationManagerImpl.buildUpgradeContext` creates this context after SCM has constructed node and pipeline managers. `SCMUpgradeFinalizer` uses it to add finalizing marks, close pipelines, finalize layout features, wait for post-finalization pipelines, and read leader term. Upgrade actions receive the same object.

State and persistence behavior: The context is immutable and owns no persistent state. It gives finalization actions access to persistent surfaces such as SCM storage VERSION files and replicated finalization metadata through its dependencies.

Dependencies and integration points: It connects generic upgrade execution with SCM internals without requiring the finalizer to hold many separate references. It is also passed to `HDDSUpgradeAction<SCMUpgradeFinalizationContext>` implementations.

Risks: Every field is required; missing builder fields fail at build time. The context stores live manager references, so finalization behavior depends on those managers still being active and leader state being current.

Test signals: Tests should assert builder null validation, getter identity, and that finalizer code receives the exact node, pipeline, storage, layout, state manager, config, and SCM context instances supplied by `StorageContainerManager`.
