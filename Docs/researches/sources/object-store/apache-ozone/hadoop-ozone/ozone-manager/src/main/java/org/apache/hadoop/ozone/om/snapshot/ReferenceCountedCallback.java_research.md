# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCountedCallback.java

Purpose: `ReferenceCountedCallback` is the callback contract used by `ReferenceCounted` when a wrapped object's total reference count reaches zero.

Important APIs and types: it exposes one method, `callback(ReferenceCounted referenceCounted)`. The raw `ReferenceCounted` parameter keeps the interface simple but sacrifices generic type precision.

Control flow and state: no implementation or state exists here. `ReferenceCounted.decrementRefCount()` invokes the callback when total count becomes zero.

Dependencies and integration points: `SnapshotCache` implements this interface and uses the callback to add an `OmSnapshot` ID to the pending eviction queue.

Risks: callback implementations must avoid heavy or blocking work if called from latency-sensitive release paths. They must also handle raw type casting carefully.

Test signals: `TestSnapshotCache` indirectly validates callback behavior by asserting cleanup queue and cache-size transitions.
