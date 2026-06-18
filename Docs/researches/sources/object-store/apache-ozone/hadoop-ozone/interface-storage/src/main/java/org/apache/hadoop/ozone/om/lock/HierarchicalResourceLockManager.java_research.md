# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/HierarchicalResourceLockManager.java

Purpose: Interface for deterministic, deadlock-resistant locking over DAG-structured OM resources.

Important APIs/types/functions: Defines `acquireReadLock(DAGLeveledResource, String)`, `acquireWriteLock(DAGLeveledResource, String)`, `acquireResourceWriteLock(DAGLeveledResource)`, `getCurrentLockedResources()`, and nested `HierarchicalResourceLock extends Closeable` with `isLockAcquired()`.

Control flow, state, and persistence: Implementations acquire resource/key locks and return a closeable handle for lifecycle management. `getCurrentLockedResources()` exposes the resources locked by the current thread. No persistence is implied.

Dependencies and integration points: Intended for resources such as FSO trees and snapshot chains, with `DAGLeveledResource` providing ordering. Implementations likely bridge to `IOzoneManagerLock`.

Risks: Correctness depends on implementations enforcing DAG order and reliable close/release semantics. Callers must close returned handles, preferably with try-with-resources, or leak locks.

Test signals: No direct implementation tests in this subset; `DAGLeveledResource` cycle test supports the ordering substrate.
