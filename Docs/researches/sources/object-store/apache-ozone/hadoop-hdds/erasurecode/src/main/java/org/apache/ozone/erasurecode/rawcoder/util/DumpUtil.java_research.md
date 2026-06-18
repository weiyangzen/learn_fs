<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java

## Purpose
`DumpUtil` provides debug formatting for raw coder matrices and chunks.

## Important APIs, Types, and Functions
It exposes `bytesToHex(byte[], int)`, `dumpMatrix(byte[], int, int)`, `dumpChunks(String, ECChunk[])`, and `dumpChunk(ECChunk)`.

## Control Flow
Hex conversion truncates by limit when requested. Dump methods print formatted matrices or chunks to standard output and use `ECChunk.toBytesArray()` for chunk data.

## State and Persistence Behavior
It has no mutable state; output is transient console/debug output.

## Dependencies and Integration Points
It depends on `ECChunk` and is used by RS coders when verbose dump is enabled.

## Risks and Test Signals
Risks include noisy stdout in production-like tests and large dump output. Tests should check formatting only indirectly through diagnostic use, with verbose dump disabled by default.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java -->
