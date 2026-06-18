# sources/object-store/openstack-swift/swift/obj/ssync_sender.py

## Purpose
Implements the sender side of Swift’s SSYNC replication protocol. It connects to a remote object server’s `SSYNC` endpoint, advertises local object hashes and timestamps for selected suffixes, receives the remote wanted set, streams PUT/POST/DELETE subrequests for requested data or metadata, and returns the set of objects that are safe to delete from handoff storage.

## Important APIs, Types, And Functions
`encode_missing(object_hash, ts_data, ts_meta=None, ts_ctype=None, **kwargs)` formats a hash, data timestamp, optional metadata/content-type timestamp deltas, offsets, and optional `durable:False` flag into the receiver’s missing-check line format. `decode_wanted(parts)` parses receiver wanted flags, defaulting legacy empty responses to data-only.

`SsyncBufferedHTTPResponse` extends Swift’s buffered HTTP response with a custom `readline()` that understands chunked transfer encoding and preserves an internal SSYNC response buffer. `SsyncBufferedHTTPConnection` binds that response class.

`Sender` is the main protocol client. Constructor inputs are a daemon with logger/timeouts/DiskFileRouter, a target node, a replication/reconstruction job, suffix list, optional `remote_check_objs`, `include_non_durable`, and `max_objects`. Its key methods are `__call__()`, `connect()`, `missing_check()`, `updates()`, `send_subrequest()`, `send_delete()`, `send_put()`, `send_post()`, and `disconnect()`.

## Control Flow
`Sender.__call__()` exits successfully with an empty deletion map when there are no suffixes. Otherwise it connects, performs missing check, and either sends updates or, when `remote_check_objs` is set, only computes which advertised objects are already in sync remotely. It catches expected timeout/replication errors as logged failures and catches unexpected exceptions so callers originally designed around rsync return codes are insulated from Python exceptions.

`connect()` opens a chunked `SSYNC /device/partition` request to the remote replication address, sends the storage policy index, optional backend fragment index and legacy node-index headers, reads the HTTP response, and rejects non-200 statuses. When sending non-durable fragments was requested, it requires the receiver’s `X-Backend-Accept-No-Commit` capability; otherwise it logs a warning and falls back to durable-only behavior.

`missing_check()` sends `:MISSING_CHECK: START`, iterates `df_mgr.yield_hashes()` for the job’s device/partition/policy/suffixes and optional fragment preferences, filters to `remote_check_objs` when supplied, sends encoded missing lines as HTTP chunks, honors `max_objects` truncation, ends the section, then reads the receiver’s wanted section. It returns `available_map` for all advertised objects and `send_map` for objects/parts the receiver wants.

`updates()` sends `:UPDATES: START`, iterates the wanted map, resolves each object hash to a DiskFile, opens it with optional non-durable fragment preferences, and sends the necessary subrequests. Wanted data becomes a PUT; if the job provides `sync_diskfile_builder` (used by the EC reconstructor), that callback can provide a rebuilt fragment stream instead of the local DiskFile. Wanted metadata newer than the data timestamp becomes a POST. Local tombstones become DELETE subrequests. DiskFile errors before bytes are sent are skipped. After `:UPDATES: END`, the sender reads the receiver’s update acknowledgment and treats any unexpected line as a replication exception.

`send_subrequest()` serializes a method/path/header block, sends it as a chunk, streams DiskFile reader chunks when present, and verifies sent bytes equal the advertised content length. `send_put()` copies datafile metadata except name/content length and adds `X-Backend-No-Commit` for non-durable sends; `send_post()` sends metafile metadata when present; `disconnect()` terminates the chunked request with a zero-length chunk and closes the connection.

## State And Persistence
The sender reads local object state through DiskFile manager `yield_hashes()` and `get_diskfile_from_hash()`. It does not mutate local object storage directly, but its return value drives handoff cleanup in `obj/replicator.py` and `obj/reconstructor.py`. `limited_by_max_objects` records partial revert progress. Remote persistence is caused by the subrequests it streams to `ssync_receiver`, which routes them through the remote object server.

In-memory state includes the available and wanted maps, remote-check filters, include-non-durable capability, max-object truncation state, and the chunked response read buffer. Network state is manually synchronized through chunk framing and SSYNC start/end markers.

## Dependencies And Integration Points
The sender depends on Swift buffered HTTP connections, DiskFile manager hash and open APIs, replication exceptions/timeouts, object-server `SSYNC`, receiver capability headers, `ssync_receiver` wire formats, and daemon fields such as `conn_timeout`, `node_timeout`, `http_timeout`, `network_chunk_size`, `_df_router`, and logger. It is used by the replicated-policy `ObjectReplicator` and the EC `ObjectReconstructor`; the latter supplies fragment-index jobs and a `sync_diskfile_builder` callback for rebuilt fragments.

## Risks And Edge Cases
The sender must keep SSYNC and HTTP chunk framing synchronized. `SsyncBufferedHTTPResponse.readline()` closes the connection on malformed chunk sizes or early disconnects because protocol state is likely lost. If a DiskFile reader yields fewer bytes than its content length, the sender aborts the session to avoid finalizing partial remote state. Legacy receiver behavior defaults wanted parts to data-only, which preserves compatibility but cannot sync standalone metadata.

`max_objects` deliberately truncates a revert pass and must prevent local cleanup from assuming completion. `remote_check_objs` performs a check-only session and should not send updates. Non-durable EC fragment replication depends on receiver capability negotiation; older receivers force durable-only behavior. Reconstructed fragment sends depend on metadata from one local fragment and byte streams rebuilt from other nodes, so content-length and ETag handling must stay aligned with object-server PUT validation.

## Test Signals
Tests should cover `encode_missing()` with meta/content-type deltas, offsets, URL quoting, and durable flags; `decode_wanted()` legacy and explicit data/meta behavior; chunked `readline()` with split lines, chunk extensions, EOF, and malformed chunks; `connect()` capability negotiation; `missing_check()` filtering, truncation, and wanted-map parsing; `updates()` PUT/POST/DELETE decisions; byte-count mismatch aborts in `send_subrequest()`; non-durable PUT headers; and check-only deletion-map behavior. Integration coverage should run sender and receiver together for replicated handoffs and EC fragment reconstruction jobs.
