# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientCreator.java

Purpose: Non-caching factory for connected `XceiverClientSpi` instances.

Important APIs/types/functions: Constructors capture configuration, optional `ClientTrustManager`, security flag, and topology-aware-read flag. `enableErrorInjection` stores a static `ErrorInjector`. `newClient(Pipeline)` chooses `XceiverClientRatis`, `XceiverClientGrpc`, or `ECXceiverClientGrpc` by pipeline replication type and connects it. `acquireClient`/`releaseClient` implement `XceiverClientFactory` without caching.

Control flow: Construction requires a trust manager when security is enabled. New clients are created per acquire and immediately connected; connection failures are wrapped as IOExceptions. Release closes the client quietly, with topology-aware read release respecting configured topology mode.

State and persistence behavior: Stores factory config and static global error injector. No client cache; users own acquired clients until release.

Dependencies and integration points: Base class for `XceiverClientManager`. Integrates pipeline types with Ratis/gRPC implementations, Ozone security, trust management, and topology-aware read behavior.

Risks: The static error injector is global and can affect all factories. For security-enabled clusters, null trust manager is rejected at construction. Unsupported `CHAINED` or unknown pipeline types throw.

Test signals: Tests should verify client type selection, security trust-manager requirement, connection failure wrapping, quiet release, and error-injection isolation.
