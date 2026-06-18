# sources/storage-engines/wiredtiger/test/suite/test_jsondump01.py

Purpose: tests `wt dump -j` and `wt load -j` utility behavior for JSON dump/load using standard dataset classes and multiple key formats.

Important APIs and functions: imports `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `compare_files`, and `suite_subprocess`. `FakeCursor` is a small iterator wrapper used to compare generated output. Scenarios combine URI/data-set types (`file:`, simple table, indexed table, complex table) with integer, recno, and string keys.

Control flow: `test_jsondump_util` creates/populates a dataset, runs the `wt dump -j` utility through `runWt`, and compares output against expected JSON-formatted cursor data. `test_jsonload_util` dumps data, drops/recreates or loads it, and validates loaded content. The exact operations depend on dataset type.

State and persistence behavior: utility dump/load is persistence-oriented: data must round-trip through on-disk dump files while preserving keys, values, indexes, and complex schema content.

Dependencies and integration points: integrates command-line `wt` utility execution, JSON dump/load format, dataset helper abstractions, file comparison helper, and subprocess test harness.

Risks and edge cases: expected dump formatting can be brittle. Complex/indexed datasets broaden coverage but also tie the test to helper dataset behavior.

Test signals: JSON dump files match expected output, `wt load -j` succeeds, and loaded datasets verify correctly.
