# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_status.py

## Purpose
This module tests `tahoe status` progress rendering, command rendering over status JSON, simple grid integration, and JSON HTTP helper validation.

## Important APIs, Types, and Functions
- `FakeStatus` supplies minimal status-object methods consumed by `marshal_json`.
- `ProgressBar` tests `pretty_progress` for ASCII and Unicode progress bars.
- `_FakeOptions` creates a temporary node directory with `private/api_auth_token` and `node.url`, and captures stdout/stderr.
- `Integration` starts a test grid, creates mutable activity, waits for the web status endpoint, and runs `tahoe status`.
- `CommandStatus` calls `do_status` with fake HTTP response sequences.
- `JsonHelpers` targets `_handle_response_for_fragment` and `_get_request_parameters_for_fragment`.

## Control Flow
Progress tests are pure function assertions. Integration setup creates a mutable file and verifies the client's web status endpoint responds before running the CLI. Renderer tests provide two JSON fragments to `do_status`: operations and counters/stats. Helper tests feed valid, null, or `BadResponse` values to response handling and validate GET/POST argument constraints.

## State and Persistence Behavior
`_FakeOptions` creates a temporary node-like directory with an API auth token and node URL. Integration tests create grid state and a mutable file to populate status data. Command renderer tests keep state in local `BytesIO`/`StringIO` response queues consumed by the fake HTTP function.

## Dependencies and Integration Points
The module integrates `allmydata.scripts.tahoe_status`, `allmydata.web.status.marshal_json`, immutable/mutable status classes, `common_http.BadResponse`, `do_http`, `GridTestMixin`, and `CLITestMixin`. It covers both direct helper APIs and the CLI-to-web-status path.

## Risks and Edge Cases
Covered risks include Unicode/ASCII progress calculations, no active/recent operations, renderer robustness over several status object types, HTTP fetch exceptions, null responses, BadResponse wrapping, and invalid GET/POST parameter combinations. Integration also protects the status command from failing when skipped operations are present.

## Test Signals
Signals are moderate to strong: pure progress output is exact, helper failures assert exceptions, and the integration test hits a real local web status endpoint. Renderer tests mainly assert no catastrophic failure, so detailed formatting regressions may not be caught.
