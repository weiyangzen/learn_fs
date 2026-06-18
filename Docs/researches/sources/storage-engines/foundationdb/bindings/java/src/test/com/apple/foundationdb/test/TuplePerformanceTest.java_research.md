# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TuplePerformanceTest.java

Purpose: CPU microbenchmark and correctness stress for Java tuple packing, unpacking, equality, hashing, packed size, and subspace pack/unpack behavior.

Important APIs and flow: tuple generators create random mixed-type, integer, floating-point, or string-like tuples including nulls, byte arrays, strings, booleans, UUIDs, versionstamps, and nested tuples. `run` warms up, then for millions of iterations serializes a random tuple, deserializes it, verifies equality both with copied items and packed representations, checks packed size, validates subspace concatenation and unpacking, and measures hash timings. It prints aggregate timing statistics.

State and persistence: no database persistence; all work is in memory. Dependencies are tuple, subspace, versionstamp, UUID, random, and byte-array utilities. Risks include very long default runtime, random coverage without deterministic seed, Unicode generation edge cases, and stdout-only metrics. Signal is strong for tuple invariants because mismatches throw runtime exceptions.
