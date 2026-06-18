# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsTest.java

## Purpose

Tests the generic manual `CompactionOptions` Java wrapper.

## Important APIs, control flow, and dependencies

The file round-trips `compression`, `outputFileSizeLimit`, and `maxSubcompactions` on `CompactionOptions`. It also verifies the default compression sentinel `DISABLE_COMPRESSION_OPTION`.

## State, persistence, risks, and test signals

No DB state is used. Native wrapper state must preserve enum and numeric values. Risks are enum byte mapping drift and long/int truncation. Signals are default assertions and exact getter values after setters.
