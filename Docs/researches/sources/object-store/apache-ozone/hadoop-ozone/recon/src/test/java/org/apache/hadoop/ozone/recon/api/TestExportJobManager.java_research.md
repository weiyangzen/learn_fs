# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestExportJobManager.java

## Purpose
Unit-level coverage for `ExportJobManager`, the Recon component that asynchronously exports unhealthy-container query results into tarred CSV downloads. It verifies submission, worker completion, chunking, duplicate-state rejection, retry after failure, queue-cap enforcement, cancellation, listing, startup cleanup, and export filename format without starting Derby or Guice.

## Important APIs, types, and functions
- Main APIs under test are `ExportJobManager.submitJob`, `getJob`, `getAllJobs`, `getQueuePosition`, `cancelJob`, and `shutdown`.
- Uses mocked `ContainerHealthSchemaManager.getUnhealthyContainersCount` and `getUnhealthyContainersCursor` as the only DB dependency.
- Uses `ExportJob` and `ExportJob.JobStatus` to observe `RUNNING`, `COMPLETED`, and `FAILED` state.
- Helper cursors are `finiteCursor(recordCount)` for deterministic rows and `blockingCursor(CountDownLatch)` for suspending worker execution.
- `listTarEntryNames` reads generated tar contents with `TarArchiveInputStream` to validate CSV part names.

## Control flow
Each test creates a manager pointed at a temporary export directory with a configurable queue size and max download count. Submission tests stub counts/cursors, submit a state such as `MISSING`, wait for asynchronous status convergence, and inspect `ExportJob` metadata and tar files. Queue and duplicate tests hold the worker inside a blocking cursor to observe the running job and queued jobs. Cancellation tests remove running and completed jobs. Startup cleanup shuts down the manager, creates stale tar/job-directory artifacts, then constructs a new manager and asserts only export leftovers were removed.

## State and persistence behavior
Runtime state is held in the manager's job tracker, queue, single worker thread, and temporary export directory. Completed jobs persist a `.tar` file and metadata path until canceled. Running jobs use a per-job working directory that should be removed on cancellation. Failed jobs should release the unhealthy-container state so a later submit for the same state can proceed. Startup cleanup removes stale tar files and job directories while preserving unrelated files.

## Dependencies and integration points
The test isolates `ExportJobManager` from the database by mocking `ContainerHealthSchemaManager`, but still exercises real file creation, tar assembly, CSV chunk naming, queue logic, worker-thread transitions, Ozone configuration keys, and cleanup logic. It depends on jOOQ record classes for fake unhealthy-container rows and Apache Commons Compress for tar inspection.

## Risks and edge cases
The largest export test synthesizes 1,000,001 rows to cross CSV part boundaries and can be slower than normal unit tests. Async polling can flake if worker timing or status transitions change. The cursor mocks only populate a small subset of unhealthy-container fields, so CSV column additions may need fixture updates. Queue-full behavior depends on the worker pulling the first job before the third submit.

## Test signals
Assertions cover total and estimated record counts, tar existence, exact three-part naming for million-row exports, empty-export completion, duplicate-state exception messages, retry after failed worker execution, queue positions, cancellation cleanup, all-job listing, startup cleanup, and `export_missing_<timestamp>.tar` filename shape.
