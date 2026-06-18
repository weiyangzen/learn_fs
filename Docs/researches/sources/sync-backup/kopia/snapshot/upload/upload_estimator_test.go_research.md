# sources/sync-backup/kopia/snapshot/upload/upload_estimator_test.go

## Purpose
Tests estimator behavior independently of full uploads, especially selection between rough volume-size estimates and classic tree scans.

## Important APIs, Types, and Functions
Defines a zap-backed `mockLogger`, `withFailedVolumeSizeInfo`, `withVolumeSizeInfo`, and `expectSuccessfulEstimation`. The single `TestUploadEstimator` table of subtests builds `mockfs` directories and `upload.NewEstimator` instances.

## Control Flow
The helper starts estimation in a goroutine, waits for callback plus `Wait`, and fails after one second. Subtests cover classic scans, rough estimates with fake volume info, rough fallback on injected error, adaptive rough or classic selection based on threshold, cancellation via context during readdir, `Estimator.Cancel` during readdir, and ignore rules excluding `file1`.

## State and Persistence Behavior
All state is in-memory mock filesystem data. No repository is created. Cancellation is triggered by `mockfs` readdir hooks.

## Dependencies and Integration Points
Depends on `mockfs`, `volumesizeinfo`, `policy.BuildTree`, `upload.NewEstimator`, and `testify/require`. It validates that `scanResults` and policy ignore integration work through the public estimator API.

## Risks
The one-second timeout can be sensitive on overloaded test hosts, but the fixture is small. Rough tests rely on injected volume info rather than platform-specific volume APIs, which is good for determinism but does not test the real provider.

## Test Signals
Successful tests signal correct estimation counts/bytes, fallback to classic scanning, zero results on cancellation, and ignore-policy compliance.
