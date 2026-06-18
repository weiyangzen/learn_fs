# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OmReadOnlyLock.java

Purpose: `OmReadOnlyLock` is an `IOzoneManagerLock` implementation for read-only snapshot metadata managers. It allows read-lock acquisition without actually locking and rejects write-lock acquisition.

Important APIs and types: All read acquire methods return `EMPTY_DETAILS_LOCK_ACQUIRED`; write acquire/release methods and read release methods return `EMPTY_DETAILS_LOCK_NOT_ACQUIRED`. Multi-user lock acquisition returns false. Hold-count and ownership checks return zero/false. `getOMLockMetrics` throws `UnsupportedOperationException`.

Control flow: Every method is a fixed response with no mutable logic.

State and persistence behavior: There is no state. The class is intended for immutable/read-only snapshot DB contexts where writes should be impossible.

Dependencies and integration points: Snapshot metadata managers can use it to satisfy APIs that expect `IOzoneManagerLock` without introducing lock overhead.

Risks and test signals: Code that expects release after read acquire to report acquired may be surprised because releases return not acquired. Any accidental write path should see lock-not-acquired and fail upstream. Tests should cover read-only manager operations, write rejection, metrics unsupported behavior, and compatibility with code that merges `OMLockDetails`.
