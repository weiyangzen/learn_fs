# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_status.py

## Purpose
Implements `tahoe status`, rendering node upload/download/mutable operation status and aggregate byte/file statistics from local node web endpoints.

## Important APIs, Types, and Functions
`_get_request_parameters_for_fragment()` builds authenticated POST request parameters. `_handle_response_for_fragment()` parses JSON and sanitizes URL-sensitive errors. `pretty_progress()` builds ASCII/Unicode progress bars. Renderers include `_render_active_upload`, `_render_active_download`, generic active/recent renderers, `render_active()`, `render_recent()`, and `do_status()`. `TahoeStatusCommand` registers CLI options.

## Control Flow
`do_status()` reads `private/api_auth_token` and `node.url` from the node directory, posts to `status?t=json` and `statistics?t=json` with the token, renders summary statistics, active operations, and recent operations, and returns 2 on retrieval/parsing errors. Rendering filters recent operations unless `--verbose` is set.

## State and Persistence Behavior
No writes. Reads local authentication and URL files from the node directory, then reads status/statistics over the node webapi.

## Dependencies and Integration Points
Depends on `BaseOptions`, `common_http.BadResponse`, `abbreviate_space/time`, and JSON status payloads from `allmydata.web.status.marshal_json`. Integrates with the node private API token mechanism.

## Risks and Edge Cases
The module overrides `print()` to replace unencodable Unicode, which protects terminals but can hide exact characters. Fetch failures are collapsed to exit code 2. `_handle_response_for_fragment()` deliberately avoids `format_http_error()` to avoid leaking sensitive `/uri/<key>` URLs.

## Test Signals
`src/allmydata/test/cli/test_status.py` covers progress bars, JSON helpers, fetch errors, renderer smoke tests, command help, and grid integration with skipped recent operations.
