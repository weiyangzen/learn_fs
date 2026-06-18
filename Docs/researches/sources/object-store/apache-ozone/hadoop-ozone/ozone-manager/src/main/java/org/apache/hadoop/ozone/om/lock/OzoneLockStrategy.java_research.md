# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockStrategy.java

Purpose: `OzoneLockStrategy` defines the strategy interface for acquiring and releasing key-related read/write locks in OM. It allows runtime selection of locking behavior by bucket layout and configuration.

Important APIs and types: It declares `acquireWriteLock`, `releaseWriteLock`, `acquireReadLock`, and `releaseReadLock`, each taking `OMMetadataManager`, volume name, bucket name, and key name. Acquire methods may throw `IOException`.

Control flow: The interface has no implementation. Concrete strategies decide whether to use bucket locks only, key-path locks, or future FSO-specific locking.

State and persistence behavior: Strategies coordinate in-memory lock state around persistent OM metadata operations. The interface owns no state.

Dependencies and integration points: `OzoneLockProvider` returns implementations, and key/file request classes use them to guard metadata reads and writes.

Risks and test signals: All implementations must pair acquisitions and releases in reverse order and release partial acquisitions on failure. Tests should apply a shared suite across strategies for read/write success, exception safety, and lock-order compatibility.
