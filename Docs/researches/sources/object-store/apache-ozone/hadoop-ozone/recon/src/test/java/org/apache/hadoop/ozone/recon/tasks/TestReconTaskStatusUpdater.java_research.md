# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestReconTaskStatusUpdater.java

Purpose: Tests intended behavior of `ReconTaskStatusUpdater`, the helper that inserts or updates Recon task status rows.

Important APIs and control flow: Setup mocks `ReconTaskStatusDao` and a mocked `ReconTaskStatusUpdater`, stubbing `updateDetails` to insert when `existsById` is false and update otherwise. Tests verify first-time insert, existing-row update after setting task status, and setter invocations for sequence number, timestamp, run status, and running flag.

State and persistence behavior: The production concept is persisted `ReconTaskStatus` rows with task name, sequence, timestamp, status, and running marker. This test uses mocked objects, so it verifies interaction shape rather than actual field mutation or DAO persistence.

Dependencies and integration points: Uses generated jOOQ DAO/POJO classes and Mockito. The updater is consumed by `ReconTaskControllerImpl` around each task run and reprocess.

Risks and test signals: Low-to-moderate signal because the updater itself is mocked, including the method under test. It documents intended insert/update branching but would not catch implementation regressions inside real `ReconTaskStatusUpdater`.
