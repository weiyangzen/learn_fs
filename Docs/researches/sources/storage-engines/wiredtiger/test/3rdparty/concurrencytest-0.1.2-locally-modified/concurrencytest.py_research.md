<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py

Purpose: Vendored, locally modified `concurrencytest` helper that adapts `testtools.ConcurrentTestSuite` to run a unittest suite across forked worker processes and report results through subunit.

Important APIs/functions: `CPU_COUNT` defaults concurrency from `multiprocessing.cpu_count`. `wait_for_children` polls child PIDs with `os.waitpid(..., os.WNOHANG)`, converts wait status to exit code when Python provides `os.waitstatus_to_exitcode`, and logs unexpected exits with the parent PID prefix. `fork_for_tests(concurrency_num)` returns a `make_tests` closure for `ConcurrentTestSuite`. `partition_tests` uses `testtools.iterate_tests` and `itertools.cycle` to distribute tests round-robin.

Control flow: `fork_for_tests` partitions the suite, clears the original suite list to release references, creates a pipe per partition, forks, and in the child closes stdin/read-end, wraps the write pipe in `TestProtocolClient` with `AutoTimingTestResultDecorator`, tags results with the child PID, runs the partition suite, and exits. The parent closes the write end, wraps the read stream as `ProtocolTestCase`, stores child PIDs, and starts a thread to reap children.

State and persistence behavior: No durable persistence. It creates OS processes, pipes, and a background thread. It mutates the input suite by clearing `suite._tests` and clears partition lists after wrapping them into process suites to reduce memory retention.

Dependencies and integration points: Unix-only `os.fork`, `os.pipe`, `os.waitpid`, `subunit`, `testtools`, `unittest`, and threading. WiredTiger's Python test runner can use this to parallelize IO-heavy tests while retaining subunit-compatible reporting.

Risks: The wait thread is not joined and sleeps for five seconds per polling loop, so process cleanup messages can lag. Mutating private `suite._tests` depends on unittest internals. Empty partitions still fork if concurrency exceeds test count. The module declares `_all__` rather than `__all__`, so intended exports are not honored by wildcard import. Windows is not supported despite a comment in `wait_for_children`.

Test signals: The `__main__` demo compares sequential and four-process execution. Stronger tests would verify partition balancing, child traceback propagation, PID tagging, child reaping, and behavior when a child exits by signal or nonzero status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py -->
