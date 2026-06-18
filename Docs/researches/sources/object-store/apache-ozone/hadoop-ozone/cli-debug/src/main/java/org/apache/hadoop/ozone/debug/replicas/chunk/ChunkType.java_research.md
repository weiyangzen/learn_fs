# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/chunk/ChunkType.java

Purpose: `ChunkType` labels erasure-coded key chunks as `DATA` or `PARITY`.

Important APIs and types: It is a two-value enum used by `ChunkKeyHandler`.

Control flow and state: There is no behavior or mutable state. `ChunkKeyHandler` chooses `PARITY` when the EC replica index is greater than the data count, otherwise `DATA`.

Dependencies and integration points: It appears in chunk-info JSON output for EC keys.

Risks and test signals: The enum is stable, but classification depends on correct one-based replica index handling. Tests should validate boundary indexes around the data/parity split.
