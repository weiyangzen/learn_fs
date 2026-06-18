# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/resource/TestLeakDetector.java

## Purpose
Tests the generic `LeakDetector` utility behavior for resources that implement `UncheckedAutoCloseable`.

## Important APIs, types, and functions
- Defines a small `MyResource` wrapper whose `close` method increments an `AtomicInteger`.
- Uses `LeakDetector.track` and close semantics to detect whether tracked resources are closed.
- Test cases are `testNoLeaks` and `testLeaks`.

## Control flow
`testNoLeaks` creates and closes a tracked resource, expecting no leak callback. `testLeaks` creates a tracked resource without closing it and relies on detector cleanup/check behavior to report the leak path.

## State and persistence behavior
State is limited to an `AtomicInteger` and detector-held resource references. There is no disk persistence.

## Dependencies and integration points
The utility sits beneath HDDS resource management paths and integrates with Ratis `UncheckedAutoCloseable` conventions.

## Risks and test signals
Leak detectors can be noisy if close tracking is wrong or silent if references are lost too early. The tests signal expected closed and leaked-resource accounting.
