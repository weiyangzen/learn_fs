# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.cc

## Purpose

This file implements the HTTP plugin's utility and runtime engine layer: HTTP-to-XRootD error mapping, header parsing, checksum digest parsing, curl handle defaults, a pollable bounded operation queue, thread-local curl handle recycling, multi-curl worker threads, continuation queues, OPTIONS chaining, redirect handling, broker socket waiting, monitoring metrics, and global curl initialization/shutdown.

## Important APIs, types, and functions

Status helpers are `HTTPStatusIsError`, `HTTPStatusConvert`, and local `CurlCodeConvert`. `HeaderParser` implements `Parse`, `Canonicalize`, `ParseDigest`, `Base64Decode`, and `ChecksumTypeToDigestName`, recording content length/range, multipart boundaries, allowed verbs, location, ETag, cache-control, and digest checksums. `GetHandle` creates a curl easy handle with user agent, optional verbose header dump, CA file/dir from XRootD env or X509 env vars, and 32 KiB buffer size.

`HandlerQueue` implements `Produce`, `Consume`, `TryConsume`, `Expire`, `GetHandle`, `RecycleHandle`, `ReleaseHandles`, `Shutdown`, and `GetMonitoringJson`. It uses a pipe as a pollable readiness FD and condition variables for bounded producers/consumers.

`CurlWorker` implements constructor setup, `Run`, `RunStatic`, `Start`, `Shutdown`, `ShutdownAll`, `ClientX509CertKeyFile`, `OpRecord`, and `GetMonitoringJson`. Static `initcontrol` calls `curl_global_init` and later shuts workers down and calls `curl_global_cleanup`.

## Control flow

Clients produce `CurlOperation` objects into the shared queue. Worker threads consume operations up to `m_max_ops`, allocate/reuse easy handles, call operation setup, optionally inject an OPTIONS operation when `RequiresOptions()` is true, and add handles to a curl multi handle. The loop polls the shared queue FD, continuation queue FD, shutdown pipe, broker FDs, and curl's own wait set at short intervals.

Completed curl messages are classified. HTTP error statuses map through `HTTPStatusConvert` and fail the operation. Successful OPTIONS operations update cache and start their parent. Successful redirects call the operation's `Redirect`, possibly starting another OPTIONS probe for unknown target capabilities. Callback-aborted transfers are mapped from `CurlOperation::OpError` to header timeout, operation timeout, slow transfer, client/server stall, or callback error. Ordinary curl errors map through `CurlCodeConvert`, with `CURLE_COULDNT_CONNECT` able to trigger one broker retry when a connection callout exists.

## State and persistence behavior

All state is process-local. `HandlerQueue` tracks operation counters and thread-local easy handles. `CurlWorker` tracks static worker list, per-verb/status metrics, connection-callout counters, and per-worker liveness timestamps. No data is persisted to disk, but `GetMonitoringJson` is intended for the factory's monitoring output path.

## Dependencies and integration points

The file integrates libcurl multi, OpenSSL BIO/EVP for digest decoding, XRootD environment/log/status/response APIs, XRootD protocol error codes, local `CurlOperation`, `VerbsCache`, `File`, and worker headers, POSIX pipes/fcntl/read/write/syscall, and optional dump logging with authorization redaction. It is central to every HTTP operation.

## Risks and edge cases

This is concurrency- and lifetime-heavy code. Queue pipe bytes must stay synchronized with deque entries, expired operations are failed after unlocking to avoid callback reentrancy deadlocks, and continuation races are explicitly handled when operations have already completed. Worker handle accounting around OPTIONS parents, redirects, broker waits, and failures is complex and can leak or double-count handles if changed carelessly. `HeaderParser::ParseDigest` has to support both standard and legacy base64 CRC32C forms. Header canonicalization rejects invalid bytes, which is good for safety but can abort on unusual server behavior.

## Test signals

Important tests should cover status and curl error mappings, header canonicalization, content-range and multipart detection, digest parsing for MD5/CRC32C, queue backpressure/expiry/shutdown, handle recycling, worker OPTIONS chaining, redirect behavior, broker wait success/failure/timeout, continuation after pause, monitoring JSON, and global shutdown. This checkout does not contain focused XrdClHttp unit tests; integration/build coverage is the main visible signal.
