# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/LeakTracker.java

## Purpose
Weak-reference token used by `LeakDetector` to track whether a resource was closed before garbage collection.

## Important APIs and types
It extends `WeakReference<Object>` and implements `UncheckedAutoCloseable`. `close()` removes the tracker from the active leak set. `reportLeak()` runs the supplied leak reporter.

## Control flow and state
The tracker keeps references to the shared active set and reporter, but only a weak reference to the resource. It is package-private and final, forcing use through `LeakDetector`.

## Dependencies and integration points
Used exclusively by `LeakDetector`. Depends on Java reference queues and Ratis `UncheckedAutoCloseable`.

## Risks and test signals
Tests should verify close suppression and reporter invocation through `LeakDetector`. The reporter should avoid strong references to the tracked object.
