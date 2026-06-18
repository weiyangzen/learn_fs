# sources/storage-engines/wiredtiger/test/suite/test_dump.py

Purpose: end-to-end `wt dump` and `wt load` coverage for files, simple tables, indexed tables, complex tables, key formats, and text/hex dump modes.

Important APIs and control flow: scenarios combine object type, key format, and dump format. The test populates a dataset, runs `wt dump` optionally with `-x`, loads into a separate home, compares `wt list`, reopens that home and checks content, reloads into original home, verifies `load -n` fails on overwrite, dumps complex-table index content, and tests `load -r` rename.

State and persistence: dump files, separate home directories, loaded metadata, table data, and index data are all validated.

Dependencies and integration: uses `suite_subprocess`, `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `shutil`, and filesystem directories.

Risks and test signals: validates utility compatibility with schema metadata and data values. Differences in value lines, missing list entries, or empty error output signal dump/load regressions.
