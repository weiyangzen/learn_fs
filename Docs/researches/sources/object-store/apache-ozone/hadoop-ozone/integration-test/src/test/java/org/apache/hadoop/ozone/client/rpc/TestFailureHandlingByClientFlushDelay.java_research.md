<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java

Purpose: This variant retests pipeline failure handling with stream-buffer flush delay and tiny test sizes. It verifies client behavior when buffered writes, explicit flushes, and pipeline shutdown interact.

Important APIs/types/functions: The fixture uses `ClientConfigForTesting` to set `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, and `BLOCK_SIZE`, plus RATIS/SCM timeout knobs. The main test uses `KeyOutputStream`, `BlockOutputStreamEntry`, SCM pipeline lookup, datanode shutdown, `OmKeyArgs`, `OmKeyInfo`, and `TestHelper.validateData`.

Control flow: `init` builds a 10-datanode cluster, creates a volume and bucket, and configures static rack mapping. `testPipelineExclusionWithPipelineFailure` creates a RATIS key sized to one block, writes and flushes one chunk, discovers the backing container and pipeline, shuts down two nodes, writes and flushes again, checks that no container or datanode entries were recorded in the exclude list at that point, writes a third copy, and closes. OM lookup then verifies that a new block replaced the original failed block and the final key size is three chunks.

State and persistence behavior: The test is focused on visible client stream state and OM key metadata. It checks block ID replacement, final data size, and full readback, but does not inspect container RocksDB directly.

Dependencies and integration points: It integrates the client flush-delay buffering path with RATIS pipeline failure classification, SCM pipeline selection, datanode shutdown, and OM close-key commit handling.

Risks: Because failure is induced between flushes, the exact point where the stream observes the pipeline failure depends on buffering thresholds and asynchronous RATIS responses. The duplicated assertion on datanodes indicates this test primarily protects final rewrite/read correctness rather than every intermediate exclude-list dimension.

Test signals: Passing means delayed-flush writes survive two-node pipeline failure, are finalized in OM with correct length, and validate through normal Ozone reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java -->
