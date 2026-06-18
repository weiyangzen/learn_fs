<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py

Purpose: Provides HTTP and Twisted Web helpers for Tahoe web tests, including body-returning requests and direct resource rendering.

Important APIs and functions: `VerboseError` extends `twisted.web.error.Error` to include response body text. `do_http(method, url, **kwargs)` performs a non-persistent `treq` request and returns response bytes. `render(resource, query_args)` renders a Twisted `Resource` against a synthetic `TahoeLAFSRequest`.

Control flow: `do_http` awaits `treq.request`, reads content, raises `VerboseError` for 4xx/5xx status codes, and returns the body otherwise. `render` builds a `DummyChannel` and request, calls `resource.render`, handles `UnsupportedMethod` as 405, waits for synchronous bytes or `NOT_DONE_YET`, then parses the HTTP wire response to return only the body.

State and persistence: Uses transient in-memory request/channel objects. No durable state is written.

Dependencies and integration points: Integrates `treq`, Twisted Web test helpers, `TahoeLAFSRequest`, `NOT_DONE_YET`, and HTTP status constants. Used by resource-level tests that avoid starting a full web server.

Risks: `render` always uses GET and minimal request fields, so resources depending on richer request state may not be represented. Splitting the raw response at `\r\n\r\n` assumes a complete HTTP header/body serialization. `do_http` carries a TODO for replacing manual status handling with `fail_for_status`.

Test signals: Exercise successful body reads, 4xx/5xx body reporting, unsupported methods, asynchronous render completion, already-finished `NOT_DONE_YET`, and invalid resource return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_web.py -->
