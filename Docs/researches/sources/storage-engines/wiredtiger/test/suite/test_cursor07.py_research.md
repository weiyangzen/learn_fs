<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor07.py

Purpose: validates log cursor visibility for logged versus non-logged tables, including records in mixed transactions and after reopen.

Important APIs and control flow: logging is enabled with small log files and dsync. The test creates one logged table and two non-logged tables, writes 7000 binary values to the logged table and one non-logged table in the same transaction, writes the other non-logged table in a separate transaction, optionally reopens, scans `log:` cursor records, and counts only log values containing the logged-table binary payload.

State, persistence, and dependencies: state includes log files, table data, and optional recovery/reopen. Dependencies are `suite_subprocess`, `make_scenarios`, `open_cursor('log:')`, transaction APIs, and binary value handling.

Integration points: covers log cursor decoding, logging disabled per table, transaction log records across file boundaries, and recovery persistence.

Risks and test signals: the test assumes payload matching is unique enough to identify logged table records. Pass signal is exactly `nkeys` logged values and no contamination from non-logged tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor07.py -->
