# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientFactory.java

Purpose: Interface for obtaining and releasing `XceiverClientSpi` connections to container pipelines.

Important APIs/types/functions: Defines general acquire/release, read-specific acquire/release, topology-aware acquire, and topology-aware release methods. Extends `AutoCloseable`.

Control flow: Implementations decide whether to cache, connect, close, or topology-select clients. Callers acquire with a `Pipeline`, use the client, then release with an invalidation hint.

State and persistence behavior: Interface has no state. Implementations such as `XceiverClientCreator` and `XceiverClientManager` own state.

Dependencies and integration points: Used by block input/output paths and higher-level Ozone clients to abstract Ratis/gRPC client creation and pooling.

Risks: Correctness depends on callers always releasing clients, especially when an implementation caches references. The invalidation and topology flags must be consistently interpreted across implementations.

Test signals: Contract tests should exercise acquire/release pairs, invalidation behavior, read-specific topology use, and close cleanup.
