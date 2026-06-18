# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2pyunit.py

## Purpose

`subunit2pyunit.py` replays a subunit v2 stream through Python's `unittest.TextTestRunner`, making subunit input visible as ordinary pyunit-style output.

## Important APIs, Types, and Functions

`main()` parses `--no-passthrough` and `--progress`, creates a `ByteStreamToStreamResult` from stdin or a named file, decorates its result with `StreamToExtendedDecorator`, optionally routes global attachments to `CatFiles(sys.stdout)`, and runs it through either `unittest.TextTestRunner` or Bazaar's `bzrlib` progress runner.

## Control Flow

`DecorateTestCaseResult` wraps the stream-backed test case so `startTestRun` and `stopTestRun` are called around the run. The wrapper function controls whether non-test global file packets are printed to stdout. Exit code is 0 when the runner result is successful, otherwise 1.

## State and Persistence Behavior

State is limited to runner/result state. The command reads stdin or a file, writes human-readable test output to stdout/stderr, and persists no files.

## Dependencies and Integration Points

It depends on `unittest`, `testtools.DecorateTestCaseResult`, `StreamResultRouter`, `StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, `subunit.filters.find_stream`, and `CatFiles`. The optional `--progress` path depends on `bzrlib`.

## Risks and Test Signals

The optional Bazaar runner is likely unavailable in modern environments. Passthrough routing must not corrupt normal test output. Validation should feed v2 streams with pass, fail, skip, and global stdout packets, checking TextTestRunner output and exit status.
