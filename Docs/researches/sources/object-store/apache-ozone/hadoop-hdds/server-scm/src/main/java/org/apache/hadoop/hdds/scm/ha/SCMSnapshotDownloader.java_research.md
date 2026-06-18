# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotDownloader.java

Purpose: Protocol-neutral contract for downloading an SCM DB snapshot from a remote SCM.

Important APIs and types: Extends `Closeable`; `download(Path destination)` returns a `CompletableFuture<Path>` for asynchronous download progress/completion.

Control flow: Implementations, currently the inter-SCM gRPC client path, write snapshot contents to the requested destination and complete the future with the downloaded path.

State and persistence behavior: Persistence is the downloaded snapshot archive/file at the destination path. The interface does not mandate temporary-file or atomic-write semantics.

Dependencies and integration points: Used by `SCMSnapshotProvider` to fetch the leader's RocksDB checkpoint during Ratis install-snapshot catch-up.

Risks and test signals: Callers must close implementations and handle asynchronous failures. Tests should cover future completion, failure propagation, close behavior, destination path correctness, and partial download cleanup in concrete implementations.
