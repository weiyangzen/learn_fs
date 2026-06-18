# sources/distributed-fs/tahoe-lafs/src/allmydata/webish.py

## Purpose
This module owns Tahoe-LAFS web server glue around Twisted Web. It customizes request parsing for uploads, applies site-wide HTTP security headers, privacy-preserving access logging, temporary-file handling for large request bodies, and service setup for both client and introducer web APIs.

## Important APIs, Types, and Functions
`FileUploadFieldStorage` subclasses `cgi.FieldStorage` to force Tahoe upload field bodies to remain bytes even when no MIME filename is supplied. `TahoeLAFSRequest` subclasses Twisted `Request`, overrides `requestReceived`, populates `fields` for POST form bodies, and applies `_tahoeLAFSSecurityPolicy`. `_get_client_ip`, `_logFormatter`, and `censor` provide request logging with capability/query redaction. `anonymous_tempfile_factory` returns a temp-file creator bound to a directory. `TahoeLAFSSite` subclasses `Site`, uses `TahoeLAFSRequest`, and chooses `BytesIO` or a real temporary file by content length. `WebishServer` wires `root.Root`, `OphandleTable`, static resources, storage plugin resources, Twisted strports, node URL persistence, and startup URL discovery. `IntroducerWebishServer` reuses the same server builder with `introweb.IntroducerRoot`.

## Control Flow
When a request completes, `TahoeLAFSRequest.requestReceived` rewinds the body, parses query args, detects POST form content types, builds lowercase CGI headers, synthesizes content length if Twisted did not provide it, and stores parsed `FieldStorage` in `self.fields`. It then sets security headers and calls Twisted's normal `process`. `WebishServer.__init__` builds a root resource tree, then starts child services. `startService` starts Twisted services, discovers the listening port/scheme through endpoint internals or old `TCPServer`/`SSLServer` objects, fills `_url`, and fires `_started`; optional node URL file writing is chained from that deferred.

## State and Persistence
Request state lives on each request object: `args`, `fields`, `path`, `processing_started_timestamp`, and response headers. Server state includes `root`, `site`, `_operations`, `_scheme`, `_portnum`, `_url`, `_listener`, and `_started`. Persistent side effects are limited to optional atomic writing of `nodeurl_path` and temporary request-body files created by the supplied factory.

## Dependencies and Integration Points
The module integrates Twisted application/service/web APIs, Tahoe `allmydata.web.root`, introducer web resources, operation handle tracking, storage plugin resources, `allmydata.util.fileutil.write_atomically`, and `strports.service`. It depends on Python `cgi.FieldStorage`, `urllib.parse`, and temp-file APIs. Static file serving is delegated to `twisted.web.static.File`.

## Risks and Test Signals
The POST parsing path depends on deprecated `cgi` behavior and a filename heuristic workaround; upload tests should verify bytes behavior for `file` fields with separate `name` fields. `censor` assumes ASCII query bytes before UTF-8 value decoding, so malformed query bytes need coverage. Twisted endpoint introspection uses private `_waitingForPort`, creating compatibility risk across Twisted versions. Privacy tests should assert `/uri/`, `/file/`, `/named/`, `uri`, and `private-key` are redacted in logs. Startup tests should cover bare numeric ports, SSL endpoints, and `nodeurl_path` atomic output.
