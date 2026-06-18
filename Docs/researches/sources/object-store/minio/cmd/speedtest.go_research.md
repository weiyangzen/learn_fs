# sources/object-store/minio/cmd/speedtest.go

## Purpose

`speedtest.go` implements MinIO admin speed tests for object I/O and local drive I/O. Object speed tests coordinate PUT/GET measurements across the cluster and optionally auto-tune concurrency. Drive speed tests run local disk throughput probes on formatted drives and return admin-facing performance summaries.

## Important APIs, types, and functions

- `speedTest` is the operation label constant.
- `speedTestOpts` carries object size, starting and current concurrency, duration, auto-tune flag, storage class, bucket name, checksum/multipart toggles, and credentials.
- `objectSpeedTest(ctx, opts)` returns a channel of `madmin.SpeedTestResult` and runs asynchronously.
- `driveSpeedTest(ctx, opts)` returns one `madmin.DriveSpeedTestResult` for the local node using `dperf.DrivePerf`.

## Control flow

`objectSpeedTest` starts a goroutine and closes its result channel safely. It initializes concurrency from `opts.concurrencyStart`; when auto-tune is enabled it caps the starting point by endpoint count, local disks per pool, a minimum of four operations, and `GOMAXPROCS`. The goroutine repeatedly asks `globalNotificationSys.SpeedTest` for per-node results at the current concurrency, sorts server results by endpoint, totals uploads and downloads, and tracks the highest GET throughput observed along with the corresponding PUT throughput.

Each iteration sends an aggregate result through `sendResult`. The aggregate computes per-second GET and PUT throughput and object rates from the best total byte counts and configured duration/object size, copies per-server upload/download stats, merges upload/download/TTFB timing samples, and annotates missing first-attempt downloads or uploads as errors. The loop stops when context is canceled, throughput drops, growth is below 2.5 percent, any server returns an error, or auto-tune is disabled. Auto-tune raises concurrency by roughly 50 percent per iteration.

`driveSpeedTest` builds a `dperf.DrivePerf` from serial/block/file sizes, filters `globalEndpoints.LocalDisksPaths()` to only paths containing the MinIO format config, and runs `perf.Run` against each formatted path's `.minio.sys/tmp` path. It returns a local endpoint URL using TLS state and node name, maps each `dperf` result to `madmin.DrivePerf`, appends ignored unformatted paths with `errFaultyDisk`, and surfaces the overall run error as a string.

## State and persistence behavior

Object speed testing does not persist data in this file; actual temporary objects and cleanup are delegated to the notification-system speed test implementation. It reads global endpoint topology, peer count, server version, and runtime settings. Results are streamed over a channel and stop respecting `ctx.Done()`.

Drive testing writes temporary performance data through `dperf` under formatted drives' MinIO tmp areas, but this file itself only selects paths and reports measurements. It reads disk format presence with `Lstat(pathJoin(localPath, minioMetaBucket, formatConfigFile))` and treats missing format config as a faulty/ignored disk in the result.

## Dependencies and integration points

The file depends on `globalNotificationSys.SpeedTest`, `globalEndpoints`, `globalNotificationSys.peerClients`, `Version`, `globalIsTLS`, `globalLocalNodeName`, MinIO path helpers, `Lstat`, and `errFaultyDisk`. External packages are `madmin-go/v3` result DTOs, `github.com/minio/dperf/pkg/dperf` for drive benchmarks, MinIO auth credentials, and `xioutil.SafeClose`.

Object tests integrate with cluster peer notification rather than directly calling S3 APIs here. Drive tests integrate with local storage layout and the admin drive speed test endpoint.

## Risks and edge cases

- Throughput division assumes nonzero duration and object size; invalid options could panic or divide by zero if validation elsewhere fails.
- The auto-tune minimum of four can exceed very small local resources, although it is later capped by `GOMAXPROCS`.
- The "best" result is selected primarily by GET throughput; a special path accepts lower GET if PUT improves, which can make reported best results reflect a hardware anomaly rather than a clean peak.
- If the first attempt yields zero uploads or downloads, the result embeds error strings but still reports the aggregate.
- `driveSpeedTest` indexes `localPaths[idx]` while iterating over `perfs`, but `perfs` corresponds to filtered `paths`; if ignored paths appear before formatted paths, reported paths can be misaligned unless `dperf` preserves a shape matching `localPaths`.
- Both tests depend on global cluster state, so unit testing requires substantial mocking or integration setup.

## Test signals

No tests for this file are included in this subset. Expected coverage should exercise auto-tune stopping conditions, zero-result error strings, context cancellation, server result sorting, invalid duration/object-size validation in callers, and drive path mapping with mixed formatted/unformatted disks.
