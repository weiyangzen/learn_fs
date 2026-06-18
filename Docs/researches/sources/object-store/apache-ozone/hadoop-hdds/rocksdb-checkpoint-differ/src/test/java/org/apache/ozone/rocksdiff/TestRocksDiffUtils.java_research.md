# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDiffUtils.java

Purpose: Focused tests for `RocksDiffUtils` prefix and SST filtering helpers.

Important APIs and types: Covers `isKeyWithPrefixPresent` and `filterRelevantSstFiles` with `SstFileInfo`, `TablePrefixInfo`, immutable maps/sets, and `getLexicographicallyHigherString`.

Control flow: One test checks prefix presence across key ranges. The parameterized test mutates an input SST map under different lookup-table sets and validates that relevant SSTs plus untracked metadata remain.

State and persistence behavior: No persistent state; the key behavior is in-place mutation of the supplied SST map.

Dependencies and integration points: These helpers are used by checkpoint differ SST filtering by table and key-prefix ranges.

Risks: Lexicographic boundaries and bucket-name prefix overlap are subtle. Missing SST metadata is intentionally retained, which favors correctness over pruning precision.

Test signals: Positive, negative, boundary, multi-table, and untracked-SST cases provide direct regression coverage.
