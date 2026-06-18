# sources/sync-backup/borg/src/borg/legacy/remote.py

Purpose: implements Borg's legacy SSH remote repository protocol for Borg 1.x repositories. `LegacyRemoteRepository` is the client proxy that starts `borg serve`, negotiates versions, batches msgpack RPC requests, reconstructs remote exceptions, and exposes repository-like methods. `RepositoryServer` is the server dispatcher for allowlisted legacy methods, path restrictions, repository lifecycle, and queued log forwarding.

Important APIs/types: `api` decorates client stubs with server-version and parameter compatibility checks. `call_many` is the core multiplexing loop for requests, responses, async responses, stderr, and remote log records. `SleepingBandwidthLimiter` limits upload writes. RPC errors map to Borg repository, locking, integrity, and path errors.

Control flow/state: construction opens an SSH or testsuite subprocess, sets nonblocking descriptors, negotiates, opens the legacy repository, and records repo ID/version. Requests are keyed by monotonically increasing `msgid`; responses are stored in `responses`, ignored async results in `async_responses`, and pending output in `EfficientCollectionQueue`. Server `serve` reads msgpack dicts, filters kwargs by target signature, executes a server or repository method, and writes msgpack result or structured exception.

Dependencies/integration: depends on `LegacyRepository`, modern `Repository` only for some exception classes, `borg_serve_log_queue`, limited unpackers, `Location`, `fslocking` errors, version helpers, and platform flags. The server enforces `--restrict-to-path` / `--restrict-to-repository` on resolved paths.

Risks: protocol compatibility is name-based and subtle; new parameters need explicit `@api` restrictions. Async `wait=False` operations require later `async_response` collection. Transport code is sensitive to nonblocking IO, subprocess shutdown, and log flushing. The stdout receive path feeds data to the unpacker twice, which is a suspicious high-risk behavior if duplicated messages appear.

Test signals: cover negotiation, version rejection, exception reconstruction via `inject_exception`, async put/delete errors, path restrictions, stderr logging, log queue flushing on close, and connection-break handling.
