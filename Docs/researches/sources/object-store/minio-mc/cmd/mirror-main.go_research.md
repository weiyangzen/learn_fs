# Research: sources/object-store/minio-mc/cmd/mirror-main.go

## sources/object-store/minio-mc/cmd/mirror-main.go

Purpose: implements `mc mirror`, synchronizing objects, prefixes, and optionally buckets from a source to a target, including watch mode, active-active mode, removals, metadata preservation, retry, Prometheus metrics, and summary output.

Important APIs and types: `mirrorCmd` defines a large CLI surface; `mirrorJob` owns watcher, status, `ParallelManager`, channels, source/target URLs, and options; `mirrorMessage` formats output; key methods are `doMirror`, `doMirrorWatch`, `doRemove`, `doCreateBucket`, `doDeleteBucket`, `startMirror`, `watchMirrorEvents`, `monitorMirrorStatus`, `mirror`, and `runMirror`.

Control flow: `mainMirror` validates encryption keys and syntax, optionally starts a `/metrics` HTTP endpoint, and repeatedly calls `runMirror` for watch/active-active modes. `runMirror` builds `mirrorOptions`, prepares clients, handles bucket-level create/delete/preserve policy work, joins the watcher, then executes a `mirrorJob`. The job lists differences from `prepareMirrorURLs`, filters by age, queues copies/removes through `ParallelManager`, and reports results through `statusCh`.

State and persistence: mutates target buckets, objects, metadata, storage class, replication-related active-active metadata, bucket policies, object lock settings, and deletions when `--remove` or active-active delete events are enabled. Metrics counters/histograms are process-global.

Dependencies and integration: integrates `objectDifference`, `bucketDifference`, `Watcher`, `ParallelManager`, `Status`, SSE key lookup, `uploadSourceToTargetURL`, retry manager, MinIO SDK retention/object-lock types, notification event types, and Prometheus.

Risks and tests: concurrency, cancellation, and watch restarts are complex. `--skip-errors` controls whether errors cancel the run; active-active loops are avoided with user-agent and metadata checks but remain sensitive. Prometheus uses global registration, which can conflict in repeated tests. No direct mirror tests are in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-main.go -->
