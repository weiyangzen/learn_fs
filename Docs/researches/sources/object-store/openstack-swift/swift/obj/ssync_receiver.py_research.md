# sources/object-store/openstack-swift/swift/obj/ssync_receiver.py

## Purpose
Implements the receiver side of Swift’s SSYNC replication protocol. The receiver runs inside the object server’s `SSYNC` response body, validates the target device/partition/policy, compares the sender’s offered object hashes and timestamps with local DiskFiles, returns wanted data/meta parts, accepts streamed PUT/POST/DELETE subrequests, routes them through `ObjectController`, and reports protocol errors back to the sender.

## Important APIs, Types, And Functions
`SsyncClientDisconnected` marks early client disconnects. `decode_missing(line)` parses sender-advertised object hash, data timestamp, optional metadata/content-type timestamp deltas, and durability into a dict. `encode_wanted(remote, local)` compares remote and local timestamp state and returns a wanted line containing `d` for data and/or `m` for metadata.

`SsyncInputProxy` wraps `wsgi.input` with timeout-aware `read_line()` and `_read_chunk()` methods. It stores the first exception and re-raises it on later reads so the receiver and object subrequests cannot continue reading from an uncertain stream. `make_subreq_input()` exposes a bounded file-like iterator for a PUT subrequest body.

`SsyncAnnotatedLogger` prefixes receiver logs with remote address and target device/partition. `Receiver` owns request initialization, semaphore/replication lock management, missing-check comparison, and update subrequest routing. Its main methods are `initialize_request()`, `_check_local()`, `_check_missing()`, `missing_check()`, `updates()`, and `__call__()`.

## Control Flow
`Receiver.__init__()` immediately calls `initialize_request()`, which sets Eventlet minimum write chunk size to zero, parses device/partition/policy, validates optional `X-Backend-Ssync-Frag-Index`, validates device/partition names, resolves the DiskFile manager, verifies the device is mounted, and wraps the request input.

`__call__()` first yields a blank line to force response headers and start the bidirectional exchange. It then tries to acquire the shared replication semaphore without blocking, takes a DiskFile replication lock for the target partition, runs `missing_check()`, then runs `updates()`. Known timeout/read/HTTP/lock errors are converted into SSYNC `:ERROR:` protocol lines when possible; client disconnects and broken reads cause early socket shutdown so the sender stops writing.

During `missing_check()`, the receiver expects `:MISSING_CHECK: START`, reads offered `hash timestamp [extras]` lines until `:MISSING_CHECK: END`, calls `_check_missing()` for each line, accumulates wanted hashes, and then emits its own `:MISSING_CHECK: START`, wanted lines, and `:MISSING_CHECK: END`. `_check_local()` opens the local DiskFile by object hash and optional fragment index, detects local tombstones, data/meta/content-type timestamps, and non-durable EC fragments. If the sender offers a durable fragment that already exists locally only as non-durable, it attempts a local commit and rechecks once.

During `updates()`, the receiver expects `:UPDATES: START`, then repeatedly parses subrequest lines of the form `METHOD PATH`, reads headers until a blank line, creates an internal `swob.Request` rooted at the target device/partition, attaches a bounded body stream for PUT, injects backend policy/replication/fragment-index headers, records replication headers to force metadata preservation, and calls `subreq.get_response(self.app)`. Successful and 404 responses count as success; other responses increment failures and may abort early if the configured failure threshold and ratio are exceeded. After draining each subrequest body, a no-failure run replies with `:UPDATES: START` and `:UPDATES: END`.

## State And Persistence
The receiver itself does not write object files directly. All persistent changes happen by routing subrequests through the object server, so PUT/POST/DELETE use normal DiskFile, async container update, expirer, timestamp, and commit semantics. `_check_local()` may make an existing EC fragment durable by opening a DiskFile writer and committing the offered data timestamp. The receiver also consumes and controls the SSYNC HTTP stream, holds a process-shared replication semaphore, and takes a per-partition replication lock.

## Dependencies And Integration Points
The receiver integrates with `obj/server.py` through `ObjectController.SSYNC()` and subrequest routing. It shares wire encodings with `ssync_sender.encode_missing()` and `ssync_sender.decode_wanted()`, uses `request_helpers.get_name_and_placement()`, DiskFile manager lookup/open/commit APIs, Swift exceptions, swob responses, Eventlet WSGI chunk errors, and object-server replication failure thresholds. Fragment-index handling is shared with EC reconstructor/reconstructor ssync flows.

## Risks And Edge Cases
Protocol synchronization is critical. Missing newlines, early EOF, bad chunk reads, malformed start/end markers, invalid methods, missing PUT content lengths, or unexpected subrequest bodies all abort the session. Because request and subrequest readers share the same underlying stream, `SsyncInputProxy`’s sticky exception behavior prevents unsafe continued reads after a failure.

Durability handling for EC fragments is subtle: a local non-durable fragment may be committed without receiving bytes if the remote advertises it as durable at the same timestamp. Failure thresholds balance avoiding wasted transfer against tolerating occasional subrequest failures. Treating 404 subrequest responses as success is intentional for idempotent deletes and tombstone races, but should remain tested. Semaphore acquisition is non-blocking, so overload returns 503 instead of queueing.

## Test Signals
Useful tests should cover `decode_missing()` timestamp delta/offset/durable parsing, `encode_wanted()` data/meta decision logic, sticky exceptions and newline enforcement in `SsyncInputProxy`, request initialization validation, non-durable-to-durable local commit behavior, missing-check protocol framing, updates subrequest parsing, metadata replication header filtering, failure threshold aborts, socket shutdown on disconnect, and semaphore/replication-lock error responses. Integration tests should pair this receiver with `ssync_sender.Sender` and object-server DiskFile fixtures for PUT/POST/DELETE replication.
