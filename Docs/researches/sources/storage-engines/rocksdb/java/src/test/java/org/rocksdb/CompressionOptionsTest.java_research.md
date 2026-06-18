# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionOptionsTest.java

## Purpose

Accessor coverage for `CompressionOptions`.

## Important APIs, control flow, and dependencies

The tests set and read `windowBits`, `level`, `strategy`, `maxDictBytes`, `zstdMaxTrainBytes`, and `enabled`.

## State, persistence, risks, and test signals

Only native options memory is used. Risks are numeric conversion errors and default `enabled` drift. Signals are exact getter values and false-to-true `enabled` transition.
