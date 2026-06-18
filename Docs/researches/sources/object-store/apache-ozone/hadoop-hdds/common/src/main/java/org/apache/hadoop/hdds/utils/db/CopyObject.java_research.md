# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CopyObject.java

## Purpose
Declares a lightweight object-level copy hook for codec cache safety.

## Important APIs, Types, And Functions
The functional interface has one method: `T copyObject()`.

## Control Flow
No control flow exists in the interface. `DelegatedCodec.copyObject()` detects this interface and delegates copying to the object itself.

## State And Persistence
No state. Implementations decide whether copying is deep or can return `this` for immutable types.

## Dependencies And Integration Points
Integrates with codec copying and DB cache isolation for mutable metadata objects.

## Risks
An implementation returning a shallow copy for mutable state can leak mutations across cache or DB table callers. Generic type misuse is possible at runtime.

## Test Signals
Tests should verify mutable implementations really detach internal collections/arrays and immutable implementations may safely return the same instance.
