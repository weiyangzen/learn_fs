# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerChecksums.java

## Purpose
Tests the value-object behavior of `ContainerChecksums`.

## Important APIs, types, and functions
- Exercises equality, hash code, and string rendering.
- Uses AssertJ/JUnit assertions against checksum fields stored by the value object.

## Control flow
The tests create equivalent and differing checksum objects, compare equality/hash behavior, and verify `toString` contains useful field content.

## State and persistence behavior
The class under test is immutable/value-like in these scenarios. There is no persistence.

## Dependencies and integration points
`ContainerChecksums` is used by SCM/container reporting logic where stable equality and readable diagnostics matter.

## Risks and test signals
Incorrect equality or hash code would break map/set usage and test diagnostics. The file gives a low-level value semantics signal.
