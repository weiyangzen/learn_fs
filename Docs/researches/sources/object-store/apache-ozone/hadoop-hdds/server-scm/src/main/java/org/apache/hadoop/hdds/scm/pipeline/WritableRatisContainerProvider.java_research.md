<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java

Purpose: `WritableRatisContainerProvider` selects a writable container from open Ratis or standalone pipelines and creates or waits for a pipeline if none can currently serve the request.

Important APIs and types: Public API is `getContainer`. Helpers include private `getContainer`, `findPipelinesByState`, and `selectContainer`. It uses `PipelineManager`, `ContainerManager`, `PipelineChoosePolicy`, `PipelineRequestInformation`, `ReplicationConfig`, `ExcludeList`, and `SCMException`.

Control flow: The provider first tries to find an OPEN pipeline and matching container under the pipeline manager read lock. If none is found, it asks the pipeline manager to create a pipeline and waits for it to become ready. If creation fails with `SCMException`, it looks for ALLOCATED pipelines and waits for one of them to open. Finally it retries container selection and throws an `IOException` with the recorded failure reason if no container can be allocated.

State and persistence behavior: This class holds no durable state. The read lock protects the selection of open pipelines and matching containers against concurrent pipeline updates. Persistent pipeline/container state is held by the managers.

Dependencies and integration points: It is the normal Ratis and standalone block-allocation path from `WritableContainerFactory`. It relies on the choose policy to order candidate pipelines and on `ContainerManager.getMatchingContainer` for owner, size, and excluded container filtering.

Risks: If an exclude list filters all pipelines, the provider intentionally retries without exclusions, which can conflict with caller expectations after retries. Available pipeline lists are mutated while selecting. Failures during wait for allocated pipelines can hide the original creation failure in the final reason string.

Test signals: Tests should cover reuse of open pipelines, pipeline creation and wait paths, fallback to ALLOCATED pipelines, exclusion fallback behavior, read-lock acquisition, policy-driven selection, and final exception messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableRatisContainerProvider.java -->
