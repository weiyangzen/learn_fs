# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common_http.py

## Purpose
Provides blocking HTTP client helpers for CLI commands that talk to a Tahoe gateway web API.

## APIs, Types, And Control Flow
`parse_url` decomposes HTTP(S) URLs into scheme, host, port, and path. `do_http(method, url, body)` accepts bytes or a seekable/readable file-like body, computes `Content-Length`, builds an `HTTPConnection` or `HTTPSConnection`, sends the body in 64 KiB chunks, and returns the response. `BadResponse` represents connection setup failure. Formatting helpers convert response status/body into printable messages, `check_http_error` maps non-2xx responses to rc 1, and `HTTPError` wraps web API failures as `TahoeError`.

## State, Persistence, And Integration
No persistent state is written. It reads optional `__TAHOE_CLI_HTTP_TIMEOUT` from the environment and uses Tahoe full version as the User-Agent. It is used by alias creation, backup, check/deep-check, slow operations, and other command modules.

## Risks And Test Signals
Risks include a simple host/port parser that does not handle all URL forms, no redirect handling except where callers accept 302, blocking network behavior, and response bodies being consumed during error formatting. It rejects Unicode request bodies to avoid ambiguous encoding. Test signals are CLI tests with fake web servers and timeout/error-path tests around web API clients.
