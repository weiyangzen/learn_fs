# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_ls.py

## Purpose

`subunit_ls.py` lists test ids from a subunit v2 stream, optionally showing timing data and `exists` declarations.

## Important APIs, Types, and Functions

`main()` parses `--times` and `--exists`, constructs a `TestIdPrintingResult`, routes global attachment packets to `CatFiles(sys.stdout)`, and runs `ByteStreamToStreamResult` over stdin or a named input file. It also uses `StreamSummary` to compute the exit status from stream outcomes.

## Control Flow

`CopyStreamResult` sends events to both the printing result and summary result. `StreamResultRouter` routes `test_id=None` packets to `CatFiles` and all other packets to the copy result. After parsing, `result.stopTestRun()` flushes active tests and `summary.wasSuccessful()` determines exit status.

## State and Persistence Behavior

State is in `TestIdPrintingResult` active tests/durations and `StreamSummary` counters. Output is textual test ids on stdout. No files are persisted.

## Dependencies and Integration Points

It depends on `testtools.CopyStreamResult`, `StreamResultRouter`, `StreamSummary`, `subunit.ByteStreamToStreamResult`, `find_stream`, `CatFiles`, and `TestIdPrintingResult`.

## Risks and Test Signals

Timing depends on timestamp packets; missing timestamps can yield zero or `None`-derived durations depending on path. The command should be validated with `exists`, `inprogress`/final status pairs, failed status exit codes, and global stdout packets.
