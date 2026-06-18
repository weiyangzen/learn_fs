# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/LockUsageInfo.java

Purpose: Simple mutable holder for per-thread lock-held start timestamps used by lock metrics.

Important APIs/types/functions: Stores `startReadHeldTimeNanos` and `startWriteHeldTimeNanos`, both initialized to `-1`, with setters and getters.

Control flow, state, and persistence: Runtime-only state. Instances are held in `ThreadLocal`s by `IOzoneManagerLock.ResourceManager`.

Dependencies and integration points: Used by `ResourceManager` to isolate read/write lock timing per thread.

Risks: Sentinel `-1` requires consumers to handle uninitialized values correctly. The class itself is not synchronized; thread safety comes from ThreadLocal usage.

Test signals: No direct tests in this subset. Indirectly exercised by lock metric implementations.
