<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java

## Purpose

`ExportJobManager` is a Guice singleton that owns asynchronous CSV/TAR export jobs for unhealthy-container records. It lets Recon submit, track, cancel, and delete exports while serializing database cursor access through a single-thread executor.

## Important APIs and Types

The main public API is `submitJob(String state)`, `getJob`, `getAllJobs`, `getQueuePosition`, `cancelJob`, and `shutdown`. It stores `ExportJob` instances keyed by job id, uses `ExportJob.JobStatus` transitions, and queries `ContainerHealthSchemaManager` using `ContainerSchemaDefinition.UnHealthyContainerStates`. Output is split into CSV parts of 500,000 records and archived via `Archiver.create`.

## Control Flow

Construction resolves the export directory from `ozone.recon.export.directory` or `{ozone.recon.db.dir}/exports`, creates it, and deletes stale directories and `.tar` files from previous Recon runs. `submitJob` rejects duplicate states already queued, running, or completed, enforces total queue size, adds the job to tracker/queue, and submits `executeExport`. The worker removes the job from `jobQueue`, marks it running, counts expected records, streams the jOOQ cursor into CSV files, archives the job directory, deletes temporary CSVs, and marks the job completed. Cancellation removes queued jobs, cancels their `Future`, marks failures, and deletes partial artifacts and final TARs.

## State and Persistence

In-memory state is held in concurrent maps plus a synchronized `LinkedHashMap` queue. Persistent state is only the local export directory: temporary job folders and final `.tar` files. Jobs do not persist across Recon process restart, and startup cleanup intentionally removes prior artifacts.

## Dependencies and Integration Points

It integrates with Recon server config, `ReconUtils` for DB directory fallback, container health persistence, jOOQ cursors, Apache Commons `FileUtils`, and lifecycle cleanup through `@PreDestroy`. API endpoints that expose export operations depend on this manager to coordinate job status and file lifecycle.

## Risks and Edge Cases

`submitJob` creates a `Future` even for all accepted jobs, so `runningTasks` contains queued tasks as well as active work. Duplicate-state checks include completed jobs until the user deletes them, which is intentional but can surprise clients. `valueOf(job.getState())` is case-sensitive and invalid states fail inside the worker rather than at submission. `Future.cancel(true)` can interrupt export, but archive creation and file I/O interruption behavior depends on called libraries. The single synchronized queue avoids nested locking, but `ExportJob` itself must be safe for concurrent reads by REST callers.

## Test Signals

Useful tests cover configured/default export directory selection, startup cleanup, duplicate-state rejection, queue limit, queue positions, cancellation before and during cursor iteration, multi-part CSV generation, TAR cleanup, invalid state handling, and shutdown interrupt behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ExportJobManager.java -->
