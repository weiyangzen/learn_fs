# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDUtil.java

## Purpose

`UUIDUtil` generates random RFC 4122 version 4 UUID bytes without constructing a `UUID` object.

## APIs and control flow

`randomUUIDBytes()` allocates 16 bytes, fills them from a thread-local `SecureRandom`, then sets version bits in byte 6 and variant bits in byte 8. The constructor is private.

## State, dependencies, and integration

State is a `ThreadLocal<SecureRandom>`. The class depends only on Java security APIs. It integrates with ID-generation paths that need raw UUID bytes for storage or protobuf fields.

## Risks and test signals

Thread-local secure random instances avoid contention but can be heavier per thread. Tests should verify length, RFC 4122 version/variant bits, non-constant output, and no shared mutable returned arrays.
