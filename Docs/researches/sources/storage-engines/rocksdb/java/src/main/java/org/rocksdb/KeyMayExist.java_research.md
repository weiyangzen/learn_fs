# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/KeyMayExist.java research

## Purpose

`KeyMayExist` is an immutable result object for RocksDB key-existence probes. It represents whether native `KeyMayExist` determined a key is absent, may exist without returning a value, or may exist with a value length.

## Important APIs and types

`KeyMayExistEnum` has `kNotExist`, `kExistsWithoutValue`, and `kExistsWithValue`. The public final fields are `exists` and `valueLength`. The constructor sets both fields, and `equals()`/`hashCode()` compare them.

## Control flow

There is no behavior beyond object construction and equality checks. Native-facing RocksDB methods can create or return this value to Java callers as a compact status carrier.

## State and persistence behavior

Instances are immutable and hold no native resources. The class does not persist anything; it only describes a point-in-time lookup signal.

## Dependencies and integration points

It depends on `java.util.Objects` for hashing. It integrates with RocksDB point lookup APIs that expose "may exist" semantics, where Bloom filters and caches can answer absence cheaply but existence can remain uncertain.

## Risks and test signals

The object deliberately exposes fields instead of accessor methods, so API compatibility depends on those names. Tests should assert equality/hash behavior, all enum states, and JNI conversion from native existence results including value length when a value is available.
