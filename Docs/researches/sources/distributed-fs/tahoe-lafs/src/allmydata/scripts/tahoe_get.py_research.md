# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_get.py

## Purpose
Implements `tahoe get`, downloading a file or cap from the Tahoe webapi to a local file or stdout.

## Important APIs, Types, and Functions
The single public entry point is `get(options)`. It resolves `options.from_file` with `get_alias()`, constructs `/uri/<rootcap>/<escaped-path>`, performs `do_http("GET", url)`, streams response chunks of 4096 bytes, and formats errors with `format_http_error()`.

## Control Flow
The command normalizes `node-url`, resolves aliases using `DEFAULT_ALIAS`, opens `to_file` in binary mode if supplied, otherwise writes to `stdout.buffer` when stdout is text, loops over response reads until EOF, and returns `0` on status 200/201 or `1` on HTTP/alias errors.

## State and Persistence Behavior
The only persistence is local output file creation when `to_file` is set. It streams from the HTTP response to avoid buffering whole downloads in memory.

## Dependencies and Integration Points
Integrates with CLI alias configuration through `allmydata.scripts.common` and Tahoe webapi `GET /uri`. It depends on `common_http.do_http` for transport and response abstraction.

## Risks and Edge Cases
Output file handles are opened directly and closed only after a successful read loop; exceptional reads could leak handles. It treats 201 as success for GET even though 200 is the expected response. Alias errors are user-facing and produce exit code 1.

## Test Signals
`test_cli.py` includes get help, normal get behavior, broken socket handling, missing default alias, and nonexistent alias coverage; `test_cp.py` and `test_mv.py` use `tahoe get` heavily for integration verification.
