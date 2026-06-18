# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakDetector.java

## Purpose
General resource leak detector using weak references and a reference queue to report resources that are garbage-collected before their tracker is closed.

## Important APIs and types
The constructor names and starts a daemon detector thread. `track(Object leakable, Runnable reportLeak)` creates a `LeakTracker`, stores it in a concurrent set, and returns it as an `UncheckedAutoCloseable` for resource close paths.

## Control flow and state
Each detector owns a daemon thread blocking on `ReferenceQueue.remove()`. When a tracked referent is GCed, the detector removes its tracker from the active set; if it was still present, it invokes the leak reporter. Closing the tracker removes it from the set and suppresses reporting.

## Dependencies and integration points
Uses `LeakTracker`, Java reference APIs, concurrent sets, atomic naming, Ratis `UncheckedAutoCloseable`, and SLF4J. Resource classes can keep the returned tracker and close it during cleanup.

## Risks and test signals
Tests should cover leak reporting after GC, no report after close, detector thread naming/daemon status, and interruption behavior. Leak reporter must not capture the original resource, or it may prevent GC and defeat detection.
