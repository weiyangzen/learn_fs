# sources/object-store/openstack-swift/swift/common/bufferedhttp.py

## Purpose
`bufferedhttp.py` provides backend HTTP client helpers optimized for Swift's many small inter-server requests. It subclasses eventlet-green HTTP response/connection classes to buffer header reads, support `100-continue`, set TCP_NODELAY, quote Swift backend paths, and normalize query strings.

## Important APIs, types, and functions
- Module initialization raises `http.client._MAXHEADERS` and eventlet green HTTP max headers to match Swift's constraint-derived header count with slack.
- `BufferedHTTPResponse` wraps a green socket, exposes a `headers` property that repairs a Python header parsing payload issue, supports `expect_response()`, handles buffered line reads in `read()`, and can hard-close the underlying real socket with `nuke_from_orbit()`.
- `BufferedHTTPConnection` sets `response_class`, records method/path, sets TCP_NODELAY after connect, encodes header names to latin-1 bytes, supports `getexpect()`, and logs response latency in `getresponse()`.
- `http_connect()` builds a backend path from device, partition, and object/account/container path, then delegates to `http_connect_raw()`.
- `http_connect_raw()` chooses `HTTPSConnection` or `BufferedHTTPConnection`, appends a normalized query string, sends request line and headers, and returns the open connection.

## Control flow
`http_connect()` ensures path/device/partition values are bytes, quotes `/<device>/<partition><path>`, and passes the encoded backend path onward. `http_connect_raw()` fills a default port, constructs the correct connection class, round-trips query strings through `parse_qsl()` and `urlencode()` with latin-1 handling, sends the request with `skip_host` when a Host header is supplied, writes all headers as strings, and calls `endheaders()` without sending a body.

`BufferedHTTPResponse.expect_response()` closes any existing file object, reopens an unbuffered reader, reads the status line, and either parses headers for `100 Continue` or stashes a lambda so later `begin()` sees the already-read non-continue status. The custom `headers` setter handles cases where parsed header payload lines were left in the message body by adding valid `Header: value` lines back to the header mapping and clearing the payload.

## State and persistence behavior
State is per-connection and per-response: sockets, file objects, method/path metadata, timing, buffered bytes, header objects, and underlying real socket references. No persistent storage is touched. The module does mutate global stdlib/eventlet header limits at import time.

## Dependencies and integration points
It depends on Swift constraints, eventlet green HTTP classes exported by `swift.common.concurrency`, Python `http.client`, socket options, urllib quoting/parsing, and logging. It is used by backend replication, updater, auditor, proxy, and storage components that make internal Swift HTTP requests to devices and partitions.

## Risks and edge cases
Import-time mutation of `_MAXHEADERS` relies on private stdlib/eventlet attributes. `nuke_from_orbit()` calls `_real_close()` on the underlying socket, a private low-level method. Header payload repair intentionally stops on malformed or folded lines and does not attempt full RFC folding support. Path/query encoding must preserve Swift's byte semantics; changing latin-1 handling can break object names or query parameters. `getresponse()` assumes `_connected_time`, `_method`, and `_path` were set by this connection's methods.

## Test signals
Tests should cover quoted backend paths for bytes/str/int partitions, query-string normalization with blank values, Host header skip behavior, header-name byte encoding, `100 Continue` and non-continue paths, buffered reads with `amt`, socket close/nuke behavior, TCP_NODELAY setup, header payload repair, and import-time max-header alignment with constraints.
