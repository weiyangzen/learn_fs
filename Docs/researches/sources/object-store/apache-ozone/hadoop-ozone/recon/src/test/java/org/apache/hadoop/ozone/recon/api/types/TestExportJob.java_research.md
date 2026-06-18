# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/types/TestExportJob.java

## Purpose
Unit-tests the `ExportJob` POJO’s small business rules: download reservation limits, remaining download count, file path to file name derivation, null file path handling, and initial status defaults.

## Important APIs, Types, And Functions
The tests call `ExportJob.isDownloadAllowed`, `tryReserveDownload`, `getDownloadCount`, `getMaxDownloads`, `getDownloadsRemaining`, `setFilePath`, `getFilePath`, `getFileName`, `getStatus`, `getSubmittedAt`, `getEstimatedTotal`, and `getTotalRecords`. Assertions use AssertJ.

## Control Flow
Each test creates a new `ExportJob("job-1", "MISSING", maxDownloads)` and exercises one behavior. Download tests reserve downloads until the limit is reached and confirm further reservations return false. File path tests set a tar filename and then null. Initial status verifies constructor defaults.

## State And Persistence
State is entirely in-memory within an `ExportJob` instance. The download count increments only through successful `tryReserveDownload` calls and never persists externally.

## Dependencies And Integration Points
This POJO likely backs export job APIs or managers that expose downloadable generated files. The test anchors assumptions those callers depend on: queued default state, positive submission timestamp, unknown estimated total as `-1`, zero records initially, and no negative remaining download count.

## Risks
The test does not cover concurrent reservations, filesystem paths with directories, or status transitions beyond the constructor default. If `ExportJob` becomes shared across threads, `tryReserveDownload` atomicity would need additional coverage.

## Test Signals
Signals include initial downloads remaining equal to max, reservation decrementing remaining count, denial at limit, remaining count staying at zero after repeated failed reservations, file name mirroring file path for simple filenames, null path clearing file name, and initial status `QUEUED`.
