<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor13.py

Purpose: large cursor-cache test suite covering cursor caching/reopen stats, inherited cursor workloads, verify/drop interactions, sweep behavior, and duplicate cursors.

Important APIs and control flow: `test_cursor13_base` reads cursor cache/reopen/sweep stats while filtering history-store noise and provides assertions around stat deltas. Several classes inherit existing cursor and checkpoint tests to run them with cache stats. `test_cursor13_reopens` toggles connection/session cache-cursor config and validates reopen/cache counts through repeated opens, dataset checks, reconfigure, and verify. Drop tests ensure cached cursors do not prevent drops once closed but open cursors do. Big/sweep tests create many URIs and randomly open/close hundreds of thousands of cursors, asserting cache/reopen and sweep stats. `cursor13_dup` duplicates positioned cursors repeatedly.

State, persistence, and dependencies: state spans cursor cache lists, dhandles, session config, stats, many table/file objects, and optional time-based sweeps. Dependencies include other test modules, `wiredtiger.stat`, datasets, random helper, and hook skips.

Integration points: covers cursor caching, data-handle lifecycle, verify/drop compatibility, session reconfigure, and stats accounting.

Risks and test signals: long-running and timing-sensitive sweep assertions can be noisy. Pass signals are expected stat deltas, successful drops after cached cursors, and no stale dhandle/cursor reuse failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor13.py -->
