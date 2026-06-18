# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.cc

## Purpose

This file implements `CopyProcess`, the orchestrator for one or more copy jobs. It validates and defaults job properties, resolves metalinks and target paths, chooses classic versus third-party fallback jobs, runs jobs serially or in parallel, performs retry policy handling, emits monitor/progress events, and cleans up registered redirectors and job objects.

## Important APIs, types, and functions

The local `QueuedCopyJob` adapts a `CopyJob` to `XrdCl::Job`. Its `Run` method reports progress begin/end, emits monitor copy begin/end events, runs the copy job, handles write-recovery retries by retargeting to `WrtRecoveryRedir`, handles generic retry for socket/timeout/threshold errors according to `CpRetry` and `CpRetryPolicy`, stores `"status"` in results, and posts an optional semaphore.

`CopyProcessImpl` stores job property lists, result-list pointers, and allocated `CopyJob*` objects.

`CopyProcess::AddJob` handles configuration jobs, validates required source/target, fills default booleans and settings, lower-cases checksum type, pulls defaults from `DefaultEnv`, logs properties, and stores the caller's result pointer.

`Prepare` validates URLs, registers metalink redirectors, handles `xrdcl.unzip` source CGI, resolves directory targets by appending source or metalink target names, marks TPC intent CGI parameters, and creates either `TPFallBackCopyJob` or `ClassicCopyJob`.

`Run` reads process parallelism from a trailing configuration job. It runs jobs sequentially in-process when `parallel == 1`, or queues `QueuedCopyJob`s into a temporary `JobManager` and waits on a semaphore when parallelism is greater than one.

## Control flow

Callers add one or more regular jobs and optionally a configuration job. `AddJob` only stores normalized properties. `Prepare` turns those properties into live job objects and performs URL/metalink/path normalization. `Run` then executes the jobs and returns the first failure status.

Retry handling is inside `QueuedCopyJob`. `errRetry` from a destination write uses `LastURL` to preserve/extend a `tried` CGI parameter and `WrtRecoveryRedir` to retarget host/port/protocol. Generic retries for socket errors, `errOperationExpired`, and `errThresholdExceeded` either enable continue mode or force overwrite depending on `CpRetryPolicy`.

## State and persistence behavior

The process owns copied `PropertyList` objects and allocated job objects, but not result lists. It persists no durable state. Side effects are job execution and redirector registry references. `CleanUpJobs` releases metalink redirectors and deletes jobs.

## Dependencies and integration points

Dependencies include constants/default environment, logging, `ClassicCopyJob`, `TPFallBackCopyJob`, `FileSystem`, `Monitor`, `Utils`, `JobManager`, `RedirectorRegistry`, and semaphores. Integration points include `xrdcp`, `XrdClFS` copy commands, third-party copy implementations, monitor subscribers, and metalink virtual redirectors.

## Risks and edge cases

The `bools` default array includes `"target"` even though target is not a boolean; this does not affect valid jobs because target was already required, but it is confusing and dangerous if validation changes. Configuration jobs are stored in the same property vector as regular jobs while `pJobResults` only has regular job entries; `Prepare` indexes `pJobResults[i]` after skipping configuration jobs, which is safe only for the expected ordering where configuration is trailing or merged separately. A configuration job inserted before regular jobs could misalign indices.

Parallel execution shares a single `CopyProgressHandler` and monitor across jobs. The CLI progress handler is mutex-protected, but custom handlers must be thread-safe. Retry mutation of property lists is in-place and assumes no other thread reads the same job properties concurrently.

`Prepare` registers metalinks and `CleanUpJobs` releases them, but if `Prepare` fails after registering some redirectors and before jobs are created for them, release coverage depends on whether corresponding jobs were pushed. Target directory inference and path appending are string-heavy and sensitive to trailing slashes and metalink target names.

## Test signals

Useful tests would cover defaults insertion, checksum type lower-casing, missing source/target, configuration job merging and ordering, target directory path resolution for regular/metalink/ZIP sources, metalink registration/release on success and failure, TPC marking, write-recovery retry URL rewriting, generic retry policy `force` versus `continue`, serial first-error return, and parallel job result aggregation.
