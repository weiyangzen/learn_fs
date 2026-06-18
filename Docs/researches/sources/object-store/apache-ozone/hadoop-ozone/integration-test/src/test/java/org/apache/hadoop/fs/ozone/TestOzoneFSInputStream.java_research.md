# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java

Purpose: verifies `OzoneFSInputStream` read semantics through Hadoop APIs and SequenceFile integration, for both replicated O3FS buckets and EC buckets.

Important APIs/types/functions: setup creates a 30 MiB random file in O3FS and an EC FSO bucket. Tests cover single-byte `read`, byte-array reads, `ByteBuffer` read, positioned `read(position, ByteBuffer)`, positioned `readFully`, invalid positions, EOF exceptions, and `SequenceFile.Reader.sync` against replicated and EC files.

Control flow: class-level setup writes known random data once. Each test opens `FSDataInputStream`, reads through a particular API, compares returned bytes and file position behavior, and closes streams. SequenceFile tests upload a resource file to Ozone then verify `sync(0)` moves to the same position as HDFS behavior.

State and persistence behavior: persists a large test file and EC bucket data in the mini cluster. Positioned reads must not mutate stream position. Invalid or beyond-EOF positioned reads return `-1` for `read` and throw `EOFException` for `readFully`.

Dependencies and integration points: uses Hadoop `FSDataInputStream`, `ByteBufferPositionedReadable` behavior through `FSDataInputStream`, `SequenceFile.Reader`, Ozone EC replication config, and `TestDataUtil` bucket creation.

Risks: large random fixture increases runtime and memory. Assertions assume multi-byte read chunks exactly match the 1 MiB temporary buffer count. SequenceFile resource availability is required.

Test signals: catches regressions in byte-level correctness, positioned read contract, EOF handling, stream position preservation, ByteBuffer support, and EC read compatibility with SequenceFile sync.
