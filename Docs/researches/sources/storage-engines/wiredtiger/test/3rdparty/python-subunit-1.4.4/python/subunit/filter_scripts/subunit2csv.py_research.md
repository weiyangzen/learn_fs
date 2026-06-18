# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit2csv.py

## Purpose

`subunit2csv.py` converts a subunit stream into CSV rows using the package's `CsvResult`.

## Important APIs, Types, and Functions

`main()` calls `run_filter_script(lambda stream: StreamToExtendedDecorator(CsvResult(stream)), __doc__)`. `CsvResult` writes `test,status,start_time,stop_time` rows as tests complete.

## Control Flow

The shared filter runner parses common passthrough/output options, opens the input stream, constructs the result factory, runs the input through the v1 protocol path by default, and exits with 0 or 1 based on result success. `StreamToExtendedDecorator` adapts stream-style events to the extended result API consumed by `CsvResult`.

## State and Persistence Behavior

The script writes CSV to stdout or the shared `--output-to` path. It does not retain persistent state beyond output rows.

## Dependencies and Integration Points

It depends on `testtools.StreamToExtendedDecorator`, `subunit.filters.run_filter_script`, and `subunit.test_results.CsvResult`. It is a CLI integration point for CI tooling that wants flat test result rows.

## Risks and Test Signals

The CSV writer expects a text stream; binary stdout wrappers can cause type mismatches if the surrounding runner changes stream mode. Coverage is indirect through `CsvResult` behavior and shared filter tests rather than a dedicated command test in this subset.
