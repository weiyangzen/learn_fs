# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacy.java

Purpose: This suite validates `NSSummaryTaskWithLegacy` for legacy bucket layout, where directories are represented as key-table entries with trailing separators and hierarchy is inferred from key names.

Important APIs and types: It uses `NSSummaryTaskWithLegacy`, `NSSummary`, `OmKeyInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `BucketLayout.LEGACY`, `ReconConstants`, `OM_KEY_PREFIX`, and shared fixture builders from `AbstractNSSummaryTaskTest`.

Control flow: `setUp` populates a legacy tree and constructs the legacy task with a flush threshold from OM configuration. Reprocess tests rebuild namespace summaries and validate two buckets plus nested directories. Process tests clear summaries, rebuild, then apply a seven-event batch for file PUT, file DELETE, file-size UPDATE, directory PUTs, directory DELETE, and directory rename.

State and persistence behavior: Persistent `NSSummary` rows are keyed by bucket/directory object IDs even though legacy hierarchy comes from key names. Reprocess records bucket file totals, directory child sets, directory names such as `dir1/dir2`, and file-size bins. Process updates file counts/sizes, child directory membership, and directory names after rename.

Dependencies and integration points: The suite exercises the legacy key-table parser used by Recon to synthesize namespace trees from flat key names. It connects OM key events with namespace summary persistence without using the FSO directory table.

Risks: Legacy directory handling is path-string sensitive, especially trailing `OM_KEY_PREFIX` and nested names. One process test comment says bucket one is empty, but the assertion expects two files due to legacy directory/file accounting. Static answer sets need clearing before assertions that reuse them.

Test signals: Stale summary cleanup, bucket file counts of `2` and `2` after reprocess, correct byte totals, file-size distribution bins, child directory set for bucket one and dir1, dir2 containing the large file, bucket two gaining file5 and dir5, updated key2 size, and dir1 rename to `dir1_new`.
