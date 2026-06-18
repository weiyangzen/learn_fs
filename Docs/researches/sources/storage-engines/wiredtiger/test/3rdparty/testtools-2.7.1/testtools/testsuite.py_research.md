<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py

Purpose: Provides vendored `testtools` suite helpers for walking, filtering, sorting, fixture-wrapping, and concurrently running `unittest`-style tests.

Important APIs/types/functions: `iterate_tests` recursively flattens suites. `ConcurrentTestSuite` runs suite partitions from `make_tests` on threads and serializes result forwarding through `ThreadsafeForwardingResult`. `ConcurrentStreamTestSuite` runs `(case, route_code)` workers and forwards `StreamResult` queue events. `FixtureSuite` wraps a suite with fixture setup/cleanup. `filter_by_ids` mutates or delegates filtering. `sorted_tests` detects duplicate case ids and returns a sorted `unittest.TestSuite`.

Control flow: Concurrent runners create one thread per generated sub-suite, push completion or stream events into a `Queue`, and stop child results if the controller raises. Runner exceptions are converted into `ErrorHolder` failures.

State and persistence behavior: State is in thread maps, queues, and suite `_tests`; there is no persistence.

Dependencies and integration points: Depends on `unittest`, `threading`, `queue`, and `testtools` result decorators. Used by vendored testtools users and WiredTiger Python tests that import the bundled library.

Risks and test signals: Filtering mutates private `_tests`; concurrent workers must honor `shouldStop`; duplicate ids intentionally raise. Exercise with duplicate-id suites, custom suite filtering, broken worker runs, and stream event ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/testsuite.py -->
