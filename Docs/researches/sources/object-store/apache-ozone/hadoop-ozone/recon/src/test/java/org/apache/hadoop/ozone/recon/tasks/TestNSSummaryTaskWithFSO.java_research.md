# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTaskWithFSO.java

Purpose: This suite validates the FSO-specific namespace summary task over OM file and directory tables. It checks reprocess and delta updates for file counts, byte totals, file-size distributions, child directories, directory names, parent IDs, and flush-threshold behavior.

Important APIs and types: It uses `NSSummaryTaskWithFSO`, `NSSummaryTaskDbEventHandler`, `NSSummary`, `OmKeyInfo`, `OmDirectoryInfo`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `ReconNamespaceSummaryManager`, `FileTable` name constants, `Pair<Integer, Boolean>`, and reflection to set private threshold/manager fields in a mocked task.

Control flow: `setUp` uses `commonSetup` with FSO layout, filesystem paths enabled, and flush threshold `3`, then constructs `NSSummaryTaskWithFSO`. Reprocess tests run `reprocessWithFSO` and inspect the seeded tree. Process tests reprocess a baseline, then submit seven events: file PUT, file DELETE, file UPDATE, directory PUTs under two buckets, directory DELETE under `dir1`, and directory rename. Flush tests inspect returned seek position and simulate flush failure.

State and persistence behavior: FSO summaries are keyed by bucket and directory object IDs. The task persists file counts and total sizes at bucket or parent-directory scope, child directory sets on parents, directory names, and parent IDs. With thresholded processing, it flushes accumulated in-memory summary maps to Recon DB in batches and returns a seek position for retry.

Dependencies and integration points: It exercises FSO OM path semantics where parent object IDs define hierarchy, file records live in the file table, and directories live in the directory table. It validates the shared namespace summary manager's batch commit behavior and the event handler's flush-to-DB path.

Risks: The flush-failure test uses Mockito on a class with private fields set by reflection, so it is brittle. Some assertions/messages around the boolean result wording are confusing, but the expected values define behavior. Static answer sets must be cleared before reuse to avoid accumulation.

Test signals: Bucket one/two file counts and byte totals, file-size bin locations, child directory sets `{dir1}`, `{dir2, dir3}`, `{dir4}`, `{dir5}`, directory names including rename to `dir1_new`, parent IDs for initial and newly added dirs, seek position `7` after threshold flushing, and controlled failure returning seek position `0`.
