<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java

Purpose: integration tests for HDDS-8565-style NSSummary cleanup when FSO deleted directory entries are hard-deleted from Recon OM metadata tables.

Important APIs: `@BeforeAll init` starts a Recon-enabled 3-datanode cluster, disables frequent OM snapshot tasks by setting long delays, enables ACLs, creates an FSO bucket, configures an Ozone filesystem root, and sets iterate batch size. `testNSSummaryCleanupOnHardDelete` creates `/memoryLeakTest` with 10 subdirs and 5 files each, syncs Recon, verifies summaries exist, deletes the tree, verifies deleted tables, simulates hard delete, and verifies cleanup. `testMemoryLeakWithLargeStructure` repeats at larger scale with 50 subdirs and 20 files each. Helpers create directory structures, sync OM to Recon, wait for `NSSummaryTask` rebuild completion, inspect `DirectoryTable`, `DeletedDirTable`, and `ReconNamespaceSummaryManager`, delete entries from deleted tables, reprocess NSSummary, and verify no deleted-dir rows or matching directory table keys remain.

Control flow and integration: tests drive actual Ozone FS operations, then directly manipulate Recon metadata tables to simulate background hard delete. They reprocess the registered `NSSummaryTask` to validate cleanup logic over current metadata.

State and persistence: static cluster, FS, client, and Recon. Recon metadata and namespace summaries persist in test DBs until cluster teardown. Tests create and delete real FSO namespace entries.

Risks and tests: `expectedDirs` and `expectedFiles` parameters are mostly unused in verification, so the tests assert cleanup presence rather than exact counts. `simulateHardDelete` deletes while iterating a table, which depends on table iterator behavior. Large test can be timing-heavy. The cleanup verification checks directory tables, not direct absence of every NSSummary object by captured object id.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestNSSummaryMemoryLeak.java -->
