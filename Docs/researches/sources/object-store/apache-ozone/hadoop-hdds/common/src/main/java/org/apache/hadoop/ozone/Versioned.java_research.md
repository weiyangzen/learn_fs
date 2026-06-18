# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/Versioned.java

## Purpose
`Versioned` is a minimal interface for objects that expose an integer version.

## Important APIs, types, and functions
- `int version()` returns the implementing object's version.

## Control flow
No control flow exists beyond implementers providing the method.

## State and persistence behavior
The interface has no state. Implementers decide whether version is static, computed, or persisted.

## Dependencies and integration points
It has no imports and can be implemented by Ozone types that need a lightweight version contract separate from richer component-version enums.

## Risks and edge cases
The interface gives no semantics for monotonicity, compatibility, unknown versions, or serialization. Callers must know the implementing type's version domain.

## Test signals
No direct tests are needed for the interface; implementer tests should verify version values and compatibility rules.
