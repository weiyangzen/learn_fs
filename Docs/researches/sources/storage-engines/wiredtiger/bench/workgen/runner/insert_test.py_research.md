<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py

Purpose: functional example/test for operation addition, multiplication, append key generation, truncate effects, error handling, and workload options help.

Important APIs and functions: local `tablename`, `show`, and `expectException`; Workgen `Operation`, `Key`, `Value`, `Table`, `Thread`, `Workload`; direct `Session.truncate`.

Control flow: create two tables; run and display a single insert workload; truncate behind Workgen's context; build multiplied operation groups across two tables and run; truncate both; mutate operation lists with `+=` and `*=` and run; print workload/thread representations; validate expected exceptions for missing value and invalid key sizing; print workload options help.

State and persistence: table contents are repeatedly inserted and truncated. The script intentionally lets WiredTiger state and Workgen's internal key memory diverge to demonstrate insert-only tolerance.

Dependencies and integration: a developer-facing Workgen sanity/example script rather than a perf run. Uses assertions and expected exceptions as test signals.

Risks: broad `except BaseException` in `expectException` catches more than ordinary failures. Some exception behavior is deferred to `Workload.run`, so invalid setup may not fail where a reader expects.

Test signals: successful RUN1-3 assertions, expected exceptions in RUN4, printed data, and options help.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py -->
