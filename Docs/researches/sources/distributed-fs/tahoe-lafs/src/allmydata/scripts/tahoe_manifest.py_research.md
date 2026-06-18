# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_manifest.py

## Purpose
Implements `tahoe manifest` streaming output and `tahoe stats` deep-statistics retrieval for Tahoe directory trees.

## Important APIs, Types, and Functions
`ManifestStreamer` subclasses `LineOnlyReceiver` to parse newline-delimited manifest records from `?t=stream-manifest`. `manifest(options)` runs it. `StatsGrabber` subclasses `SlowOperationRunner`, overrides `make_url()` for `?t=start-deep-stats`, and formats count/size/histogram results in `write_results()`. `stats(options)` runs the stats operation.

## Control Flow
Manifest mode resolves the target alias, posts to `stream-manifest`, reads chunks, either writes raw bytes to stdout or feeds Twisted line parsing. Each line is JSON-decoded unless it begins with `ERROR:`; selected fields are printed according to `storage-index`, `verify-cap`, `repair-cap`, or default cap/path mode. Stats mode uses the slow-operation runner to poll an operation handle and then prints selected counters and histograms.

## State and Persistence Behavior
No local persistence. It streams server output incrementally, preserving memory for large trees. `ManifestStreamer.rc` accumulates error state when server-side stream lines indicate errors.

## Dependencies and Integration Points
Depends on Tahoe webapi `stream-manifest` and deep-stats operation endpoints, `SlowOperationRunner`, `encodingutil.quote_output`/`quote_path`, and `abbreviate_space_both`.

## Risks and Edge Cases
Malformed stream JSON produces stderr errors but does not necessarily abort the stream. Raw mode writes to `stdout.buffer`, so tests/options must provide binary-capable stdout. HTTP 302 is accepted for manifest. Stats output assumes certain keys, while optional keys are skipped.

## Test Signals
`test_cli.py` includes manifest help, missing alias/nonexistent alias handling, stats command help, stats missing alias handling, and integration around deep traversal.
