# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithLegacyOBSLayout.java

Purpose: This suite verifies `NSSummaryTaskWithLegacy` behavior when filesystem paths are disabled and flat OBS-style data is processed through the legacy task path. It is a compatibility/regression test for object-store layout semantics in the legacy handler.

Important APIs and types: It uses `NSSummaryTaskWithLegacy`, `BucketLayout.LEGACY`, `NSSummary`, `OmKeyInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `ReconConstants`, `OM_KEY_PREFIX`, and the OBS population helper from `AbstractNSSummaryTaskTest` with `isOBS` true and filesystem paths disabled.

Control flow: `setUp` builds two flat buckets using OBS-style population but constructs the legacy task. Reprocess tests rebuild and validate the flat bucket totals. Process tests clear and rebuild, then apply PUT events for key6 and a slash-heavy key7, DELETE for key1, and UPDATE resizing key2.

State and persistence behavior: The namespace summary table contains only bucket-level file totals and no child directories. Reprocess persists three files in bucket1 and two in bucket2. Process preserves flat object-store semantics: key insertions, deletion, and resizing alter bucket counts, byte totals, and size bins without creating directory summaries despite embedded slashes.

Dependencies and integration points: This covers the interaction between legacy task logic, disabled filesystem paths, and object-store-style keys. It guards against interpreting OBS keys as hierarchical directories when the compatibility path is used.

Risks: The setup uses `BucketLayout.LEGACY` while the class name refers to OBS layout, so the test intent depends on the fixture flags more than the local `getBucketLayout` name. It duplicates many assertions from the OBS-specific task suite, which can drift if the two compatibility paths intentionally diverge.

Test signals: Bucket counts `3` and `2` after reprocess, expected byte totals, bins `{0,1,40}` and `{0,2}`, no child dirs, counts `3` and `3` after process, updated bucket sizes including key7 and resized key2, and bins `{1,3,40}` and `{0,2,3}`.
