<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_schema03.py

Purpose: stress-tests complex, predictably random schema combinations: multiple tables, column groups, indexes, creation orders, connection restarts between phases, and index validation after incremental population.

Important APIs/types/functions: helper types `tabconfig`, `cgconfig`, and `idxconfig` generate table formats, keys, values, column group assignments, and index keys. `test_schema03` uses `suite_random`, `wtscenario.quick_scenarios`, resource limit changes, `TieredConfigMixin`, `session.create`, `reopen_conn`, and cursor search/iteration helpers.

Control flow: scenarios choose table count, column-group count, index count, table/index extra args, and restart points. The test builds each table config, assigns columns to groups and indexes, creates tables, creates column groups and indexes in phases, optionally reopens after each phase, populates a partial batch, creates late indexes, populates the rest, and validates every primary and index row.

State and persistence behavior: state spans schema metadata, generated key/value formats, current table entry counts, and reopen checkpoints after selected schema or data operations. It explicitly raises file descriptor limits because many tables and indexes can be open.

Dependencies/integration points: exercises the schema API, metadata persistence, secondary index backfill, file-type tables, tiered storage configs, and Python resource handling. Risks include high scenario complexity, known limitations around column groups after indexes, and Unix-only resource APIs; signals are exact row counts and successful indexed search for every generated entry.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_schema03.py -->
