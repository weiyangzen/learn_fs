# sources/object-store/openstack-swift/swift/common/http_protocol.py

Purpose: customizes eventlet's WSGI HTTP protocol for Swift's proxy/server edge behavior, including request parsing, header quirks, error responses with transaction IDs, eventlet compatibility fixes, and optional HAProxy PROXY protocol support.

Important APIs/types/functions: `SwiftHttpProtocol` overrides request logging, message logging, `parse_request`, `get_environ`, request-state handling, and `send_error`. Its nested `MessageClass` suppresses default content type. `SwiftHttpProxiedProtocol` consumes the first PROXY protocol line, rewrites client/server address metadata, and then delegates normal HTTP handling.

Control flow: `parse_request` decodes the raw line as ISO-8859-1, splits on literal spaces, validates HTTP version, rejects HTTP/2+, strips absolute URI scheme/host to a path, parses headers with eventlet's green HTTP parser, handles connection semantics, and processes `Expect: 100-continue`. `get_environ` compensates for Python/email parser payload bugs by recovering header lines from payload text, updating `headers_raw`, WSGI variables, chunked/content-length flags, and continue handling. `send_error` obtains or generates a transaction ID, logs, sends a close response, omits bodies for no-body status classes, and adds Swift request ID headers. The proxied protocol validates `PROXY TCP4/TCP6` or `UNKNOWN`, updates addresses, or sends a 400 and stops processing.

State and persistence: per-connection/request state includes parsed command/path/version/headers, close flags, connection state, client/proxy addresses, and logger transaction ID. No durable persistence.

Dependencies and integration: depends on Swift concurrency wrappers for eventlet WSGI/websocket/HTTP parser, Swift transaction ID generation, HTTP constants, and `html.escape`. It is selected by Swift WSGI server setup when serving HTTP or PROXY-protocol traffic.

Risks: request parsing is security-sensitive; compatibility workarounds for Python email parsing and eventlet state changes must track upstream behavior; absolute URI stripping affects proxy-style requests; PROXY parsing trusts the immediate peer to provide client address data; error output must avoid XSS and body-forbidden statuses. Tests should cover malformed versions, header limits, header payload recovery, expect-continue, no-body errors, transaction ID headers, and valid/invalid PROXY lines.
