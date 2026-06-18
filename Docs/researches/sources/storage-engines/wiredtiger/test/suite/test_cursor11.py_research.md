<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor11.py

Purpose: tests cursor key/value/position state after remove and insert operations.

Important APIs and control flow: scenarios cover integer, record-number, and string keys over file, simple table, index table, and complex table datasets. Tests remove using a positioned cursor, remove without position, remove by setting a key after having a position, and insert a new key. They assert which state remains: positioned remove keeps key/position but value is unavailable, while unpositioned remove, keyed remove, and insert leave no usable key/value/position and next iteration starts correctly.

State, persistence, and dependencies: state is dataset content plus cursor internal key/value/position flags. Dependencies are dataset helpers, `make_scenarios`, `wiredtiger` exceptions, and cursor navigation APIs.

Integration points: covers WT_CURSOR post-operation contract, including indexes and complex tables.

Risks and test signals: expectations differ subtly by operation path. Pass signals are correct errors for unavailable key/value and successful subsequent iteration from expected records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor11.py -->
