<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java -->
# Research: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java

Purpose: Provides simple key/value helper conversions for JMH benchmarks, including UTF-8 string-to-byte conversion and generated key lists.

Important APIs/types/functions: `ba(String)`, `str(byte[])`, `keys(int from, int to)`, and `keys(List<ByteBuffer> keyBuffers, int from, int to)` are the public helpers.

Control flow: `ba` and `str` convert using UTF-8. The byte-array `keys` method allocates a list and fills it with `keyN` byte arrays. The ByteBuffer overload reuses provided buffers by clearing, writing `keyN`, flipping, and returning a sublist-like newly allocated list of prepared buffers.

State and persistence behavior: No persistent state is owned. The ByteBuffer overload mutates caller-provided buffers, including position/limit, so those buffers are stateful inputs to later RocksDB JNI calls.

Dependencies and integration points: Used by JMH comparator/get/multiget/put benchmarks. Depends on Java `StandardCharsets.UTF_8`, `ByteBuffer`, and collection classes.

Risks and edge cases: Generated keys are not padded here, so callers that stored fixed-width padded keys must ensure lookup keys match. The ByteBuffer helper does not check capacity, so too-small buffers will throw `BufferOverflowException`.

Test signals: Conversion round trips, expected key list contents, and ByteBuffer position/limit after `flip` are useful low-level checks. Benchmark value-size assertions indirectly test key generation consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jmh/src/main/java/org/rocksdb/util/KVUtils.java -->
