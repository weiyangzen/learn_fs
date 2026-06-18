<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java

## Purpose
This test-side `DumpUtil` duplicates debug formatting helpers for matrix/chunk dumps used by tests.

## Important APIs, Types, and Functions
It exposes `bytesToHex`, `dumpMatrix`, `dumpChunks`, and `dumpChunk`.

## Control Flow
It formats bytes as hex and prints chunks/matrices to stdout when tests enable dumping.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It depends on `ECChunk` and is used by `TestCoderBase` diagnostics.

## Risks and Test Signals
Risks are duplicated implementation drift from main `rawcoder.util.DumpUtil` and noisy test output. Test signal is primarily developer diagnostics during failing erasure-code tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java -->
