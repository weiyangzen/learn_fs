# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/OzoneClientTestUtils.java

## Purpose
`OzoneClientTestUtils` contains shared test helpers for Ozone client tests. In this subset it provides key-content assertions.

## Important APIs, Types, And Functions
`assertKeyContent(OzoneBucket, String, String)` converts the expected string to UTF-8 bytes and delegates to the byte-array overload. `assertKeyContent(OzoneBucket, String, byte[])` reads the key from the bucket, asserts the read bytes equal the expected content, and returns `bucket.getKey(keyName)` for further checks.

## Control Flow
The helper opens an input stream with try-with-resources, reads exactly the expected number of bytes using Commons IO `IOUtils.readFully`, performs a JUnit array assertion, then fetches key details.

## State And Persistence Behavior
The class is stateless and has a private constructor to prevent instantiation.

## Dependencies And Integration Points
It depends on `OzoneBucket`, `OzoneKeyDetails`, Commons IO, UTF-8, and JUnit assertions. It is intended for tests that need both content verification and returned key metadata.

## Risks And Edge Cases
It reads only `expected.length` bytes and does not assert EOF afterward, so trailing bytes would not be detected by this helper alone.

## Test Signals
Compilation and any tests importing this utility validate it. Within this work item, similar explicit readback assertions are implemented directly in the tests.
