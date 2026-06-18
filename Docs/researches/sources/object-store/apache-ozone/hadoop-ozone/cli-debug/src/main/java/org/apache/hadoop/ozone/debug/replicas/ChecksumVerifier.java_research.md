# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ChecksumVerifier.java

Purpose: `ChecksumVerifier` implements the `checksum` replica verification check by streaming a block from a specific datanode and relying on the client read path to validate checksums.

Important APIs and types: It implements `ReplicaVerifier`, uses `BlockInputStreamFactoryImpl`, `OzoneClientConfig`, `Pipeline.copyForReadFromNode`, `IOUtils.copyLarge`, `NullOutputStream`, and `OzoneChecksumException`.

Control flow: `verifyBlock` builds a single-datanode read pipeline, opens a block input stream with the key location token and replication config, copies the entire stream to a null sink, returns pass on completion, returns `failCheck` when the root cause is an `OzoneChecksumException`, and returns `failIncomplete` for other IO failures.

State and persistence behavior: It performs no writes. It holds configuration and container client manager state for repeated checks.

Dependencies and integration points: It is selected by `ReplicasVerify --checksums` and exercises the same client-side checksum path used by data reads.

Risks: Full data streaming can be expensive for large key sets. Only IO exception causes are inspected, so nested checksum causes outside the immediate cause may be missed. Operational read failures are incomplete rather than data failures.

Test signals: Tests should cover checksum exception classification, non-checksum IO classification, successful stream drain, and single-datanode pipeline selection.
