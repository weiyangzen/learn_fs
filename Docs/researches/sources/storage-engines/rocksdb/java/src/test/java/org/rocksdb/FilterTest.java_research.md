# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FilterTest.java

## Purpose

Smoke-tests Java filter policy construction and attachment to options.

## Important APIs, control flow, and dependencies

The test creates an `Options` object, then creates `BloomFilter` instances with default arguments, bits-per-key, and bits-per-key plus block-based mode, setting each through options where applicable.

## State, persistence, risks, and test signals

No DB is opened. The important state is native filter allocation and option ownership. Risks are JNI constructor drift and premature filter disposal while options hold references. Successful construction and try-with-resources cleanup are the signals.
