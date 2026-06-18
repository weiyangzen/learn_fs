# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/ReferenceCounted.java

Purpose: `ReferenceCounted<T>` wraps an object and tracks references to it, including per-thread counts, so snapshot cache entries can be closed only after all users release them.

Important APIs and types: `get()` returns the wrapped object. `incrementRefCount()` and `decrementRefCount()` update counts. `getTotalRefCount()` and `getCurrentThreadRefCount()` expose counters. The constructor accepts `disableCounter`, in which case counter methods return `-1`, and a `ReferenceCountedCallback` parent.

Control flow: normal mode initializes a `ConcurrentHashMap` from thread ID to count and an `AtomicLong` total. Increment creates a thread entry, synchronizes on `refCountLock`, increments the thread count and total, and checks overflow. Decrement checks that the current thread holds a positive reference, synchronizes, decrements/removes the thread entry, decrements total, checks underflow, and invokes `parentWithCallback.callback(this)` when the total reaches zero.

State and persistence behavior: all state is in-memory. It does not close the wrapped object itself; the callback owner decides what zero references mean.

Dependencies and integration points: it uses Guava `Preconditions` and is used by `SnapshotCache` to wrap `OmSnapshot` DB handles. The callback enqueues entries for eviction after total ref count reaches zero.

Risks: each decrement must happen on the same thread that incremented; releasing from a different thread fails. Callback invocation occurs outside the synchronized block but immediately after total reaches zero. Disabled-counter mode bypasses safety and should only be used where reference accounting overhead is intentionally avoided. The class is package-private, limiting misuse outside snapshot package.

Test signals: `TestSnapshotCache` indirectly exercises reference count behavior through auto-closeable snapshot suppliers, pending eviction, and cleanup.
