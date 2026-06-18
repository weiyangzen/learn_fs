<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor14.py

Purpose: stress-tests opening more than 64K cursors on a single data source.

Important APIs and control flow: scenarios cover file/table, row/record-number keys, and simple/complex datasets. The test populates 100 records, then loops 66000 times opening a cursor on the same URI without retaining or explicitly closing each handle.

State, persistence, and dependencies: persistent state is the populated dataset; transient state is a very large sequence of cursor opens in one session. Dependencies are `SimpleDataSet`, `ComplexDataSet`, `make_scenarios`, and cursor allocation internals.

Integration points: targets cursor id/handle limits and session cursor allocation paths beyond 16-bit thresholds.

Risks and test signals: because cursors are not stored, Python lifetime/garbage collection may affect actual simultaneous open count. A pass is no exception during the 66000 opens; failure would suggest cursor id overflow, resource leak, or allocation limit regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor14.py -->
