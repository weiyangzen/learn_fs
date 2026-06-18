
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestMultiDigestInputStream.java

Purpose: tests `MultiDigestInputStream`, which reads data while updating one or more `MessageDigest` instances.

Important APIs and control flow: parameterized `testRead` validates empty and non-empty streams with MD5, SHA-1, and SHA-256. `testOnOffFunctionality` disables digest updates and expects the empty digest. `testOnOffWithPartialRead` verifies only bytes read while enabled affect the digest. `testResetDigests` clears digest state after partial reads. `testDigestManagement` validates `getAllDigests`, adding, replacing, removing, missing lookup, and post-read digest correctness.

State, dependencies, integration: state is held by the stream under test in digest maps and enabled flag. Uses `ByteArrayInputStream`, Apache IOUtils, and Java security digests. Relevant to upload checksum/Content-MD5 handling.

Risks and test signals: tests digest state after calling `digest()`, which finalizes each `MessageDigest`; repeated checks need fresh digest state. The suite covers normal read and byte-array read paths but not mark/reset.
