# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filters.py

## Purpose

`filters.py` contains shared plumbing for command-line subunit filters: common options, input stream selection, protocol-version dispatch, passthrough routing, and result-based filtering.

## Important APIs, Types, and Functions

`make_options(description)` defines `--no-passthrough`, `--output-to`, and `--forward`. `run_tests_from_stream()` consumes v1 or v2 input and drives a result object. `filter_by_result()` wires input, passthrough, forwarding, output selection, and a result factory. `run_filter_script()` implements the standard CLI lifecycle and exit-code policy. `find_stream(stdin, argv)` returns stdin or opens exactly one binary file.

## Control Flow

For protocol v1, `run_tests_from_stream` constructs `ProtocolTestCase` with passthrough and forward streams. For protocol v2, it builds a `ByteStreamToStreamResult`, optionally wraps output forwarding with `StreamResultToBytes`, `CopyStreamResult`, or `StreamResultRouter`, and optionally routes non-test packets through `CatFiles` or a v2 serializer. All paths call `result.startTestRun()`, run the test case, and call `result.stopTestRun()`.

`filter_by_result` chooses passthrough behavior from boolean flags and protocol version, opens output if requested, runs the stream, and closes the output file. `run_filter_script` parses common options and exits 0 if the final result is successful.

## State and Persistence Behavior

The module is mostly stateless. It opens input/output files and writes transformed streams or reports. It may drop, unwrap, or forward non-subunit input depending on flags.

## Dependencies and Integration Points

It depends on `testtools.CopyStreamResult`, `StreamResult`, `StreamResultRouter`, public subunit v1/v2 adapters, `DiscardStream`, and `CatFiles`. Nearly every `filter_scripts` module uses this shared layer.

## Risks and Test Signals

Forwarding subunit while also transforming can double-report if used incorrectly; the docstring warns not to set `forward_stream` when transforming. v1 and v2 passthrough semantics differ. `test_filters.py` validates `read_test_list` interaction and `find_stream`; `test_subunit_filter.py` validates command passthrough behavior over v2 streams.
