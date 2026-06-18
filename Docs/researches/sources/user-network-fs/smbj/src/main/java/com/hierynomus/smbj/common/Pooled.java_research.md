# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Pooled.java

Purpose: `Pooled` provides reference-count style leasing for reusable objects such as `Connection`.

Important APIs and control flow: instances start with one lease. `lease()` increments and returns `this` if the previous count was positive, otherwise returns null. `release()` decrements and returns true when the count reaches zero or below.

State, dependencies, and integration: it uses an `AtomicInteger`; subclasses use the generic self type.

Risks: `lease()` increments even when the object is already closed, making the counter less intuitive after zero. Multiple releases can drive negative counts. Tests should cover concurrent lease/release behavior, close-on-last-release, and no resurrection after close.
