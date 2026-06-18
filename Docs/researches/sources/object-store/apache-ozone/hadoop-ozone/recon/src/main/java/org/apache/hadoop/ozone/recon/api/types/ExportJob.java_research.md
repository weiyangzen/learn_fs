# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/types/ExportJob.java

## Purpose
In-memory state object for asynchronous CSV export jobs, including lifecycle timestamps, progress, file exposure, queue position, and download limits.

## Important APIs, Types, And Functions
declares `ExportJob`, `JobStatus`; key fields include `jobId`, `state`, `status`, `submittedAt`, `startedAt`, `completedAt`, `totalRecords`, `estimatedTotal`, `filePath`, `fileName`; important methods include `getJobId`, `getState`, `getStatus`, `getSubmittedAt`, `getStartedAt`, `getCompletedAt`, `getTotalRecords`, `getEstimatedTotal`, `getFilePath`, `getFileName`, `getErrorMessage`, `getProgressPercent`.

## Control Flow
`setStatus` stamps start/completion times once; `setFilePath` exposes only the filename; `tryReserveDownload` uses an atomic compare-and-set loop to enforce max downloads under concurrency.

## State And Persistence Behavior
State is in-memory job state: lifecycle timestamps, counters, file path/name, and atomic download reservations. It is not itself durable, so restart behavior depends on the export service around it.

## Dependencies And Integration Points
Integrates with Jackson. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are in-memory lifecycle loss on restart, progress overflow/truncation for very large estimates, and callers using `isDownloadAllowed` instead of atomic reservation for enforcement.

## Test Signals
Tests should cover status transitions, progress math, filename extraction, and concurrent download reservation limits.
