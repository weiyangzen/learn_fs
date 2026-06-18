# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/CompositeKey.java

## Purpose
Efficient composite map key that avoids allocating concatenated string keys for multiple key components.

## Important APIs and types
`combineKeys(Object[] components)` returns the sole component directly for length one, otherwise creates a `CompositeKey`. Equality and hash code are based on `Arrays.equals` and `Arrays.hashCode` of the component array.

## Control flow and state
The constructor stores the component array reference and precomputes hash code. There is no defensive copy.

## Dependencies and integration points
Used wherever volume/bucket/key or similar multi-part keys need hash-map lookup without string concatenation.

## Risks and test signals
Tests should cover one-component passthrough, multi-component equality, hash code consistency, null components, and mutation of the input array or mutable component objects. Because no copy is made, callers must not mutate the array after construction.
