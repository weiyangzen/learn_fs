# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.cc

## Purpose

This file implements the shared `CurlOperation` base behavior for all HTTP operations. It owns libcurl handle setup/cleanup, header parsing, response-info collection, redirects, adaptive timeout and transfer-rate checks, client certificate setup, connection-broker callouts, fake DNS mappings for preconnected sockets, operation statistics, and generic failure delivery.

## Important APIs, types, and functions

`CalculateExpiry` converts a relative `timespec` timeout to a steady-clock deadline with a 30-second default. The two `CurlOperation` constructors accept relative or absolute header expiry. `Setup` binds common libcurl options, callbacks, URL, X.509 credentials, progress callback, and optional connection callout plumbing. `FinishSetup` applies normal headers or header-callout-generated headers, treating callout `Content-Length` specially as `CURLOPT_INFILESIZE_LARGE`.

`HeaderCallback` and `Header` feed `HeaderParser` and append completed response header maps to `ResponseInfo`. `Redirect` rewrites relative locations, reconfigures TLS client certs, resets parser/timing state, and may create a new connection callout for the redirected target. `HeaderTimeoutExpired`, `OperationTimeoutExpired`, `TransferStalled`, `StatisticsReset`, `SetPaused`, `FailCallback`, and `Fail` provide timeout/error accounting and final response delivery.

The socket callbacks `OpenSocketCallback`, `SockOptCallback`, `CloseSocketCallback`, `WaitSocketCallback`, `StartConnectionCallout`, and `CleanupDnsCache` implement broker-provided connected sockets. Thread-local maps generate fake `169.254.x.y:port` endpoints so curl's `CONNECT_TO` can route a hostname to a broker socket without normal DNS.

## Control flow

Each concrete operation is created with a handler and target URL, then a `CurlWorker` calls `Setup` and `FinishSetup`. As curl receives headers, `HeaderParser` updates status, content metadata, allowed verbs, redirects, digests, and response-info maps. During transfer, `XferInfoCallback` checks header deadline, whole-operation deadline, stall interval, and exponentially weighted average transfer rate; returning non-zero makes curl report an aborted callback, which the worker later converts using `GetError`.

Redirect handling resets per-request state and updates `CURLOPT_URL`; when a connection broker is configured, redirects may create a fresh broker callout and fake DNS mapping. Release resets socket, TLS, header, and connect-to options and releases the easy handle back to the worker.

## State and persistence behavior

There is no disk persistence. Process-wide state includes static stall interval and minimum transfer rate configuration. Thread-local fake-DNS maps and refcounts persist across operations in a worker thread until entries are unused and older than one minute. Each operation stores response headers, error code, callback error, curl error buffer, timeout timestamps, bytes since last statistics reset, pause duration, callout state, and the owned easy handle while active.

## Dependencies and integration points

The file depends on libcurl, XRootD status/response/log/default environment APIs, `XrdCl::URL`, POSIX sockets, `getrandom` or `arc4random`, and local connection/header callout interfaces. It is the base layer consumed by all operation-specific `.cc` files and by `CurlWorker` in `XrdClHttpUtil.cc`.

## Risks and edge cases

The fake DNS mechanism is intentionally intricate: refcount and reverse-map bugs could leak entries or close valid sockets. Some callback paths throw or call `Fail` after partial curl setup, so worker cleanup must avoid double-freeing handles. Header-callout `Content-Length` parsing uses `stoull` without local error handling. Adaptive slow-transfer failures depend on the configured minimum rate and stall interval and can abort slow but healthy transfers. Redirect state must keep response-info from prior responses while resetting parser state for the next request.

## Test signals

High-value tests should cover header parsing into response-info, redirect URL rewriting including relative locations, callback failures, timeout classifications, pause-duration accounting, slow-transfer thresholds, connection callout success/failure/timeout, fake DNS cleanup, and handle release reset behavior. Runtime worker metrics and adjacent operation tests are the main current signals; no focused base-operation unit tests were found.
