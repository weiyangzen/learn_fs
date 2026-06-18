# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BytewiseComparatorRegressionTest.java

## Purpose

Regression coverage for Java bytewise comparator behavior after historical ordering bugs. It verifies that Java `BytewiseComparator`, the default comparator, and `BuiltinComparator.BYTEWISE_COMPARATOR` order bytes as unsigned bytewise keys, then checks `SstFileWriter` can write SST keys that previously exposed the same comparator issue.

## Important APIs, control flow, and dependencies

The tests use `Options.setComparator`, `RocksDB.open`, `RocksIterator`, `SstFileWriter`, `EnvOptions`, `Slice`, and helper hex parsing. `performTest` writes three byte-array keys, iterates from the first key, and asserts the exact order. `testSST` writes two hex-decoded binary keys to an external SST with a Java comparator.

## State, persistence, risks, and test signals

Temporary DB and SST folders isolate persisted state. The key risk is signed-byte comparison in Java or inconsistent Java/C++ comparator naming causing sorted iteration or SST construction failures. Signals are exact array-order assertions and successful `SstFileWriter.finish()` for non-text binary keys.
