<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb_test.go -->
# sources/storage-engines/pebble/internal/mkbench/ycsb_test.go

Purpose: fixture tests for YCSB parsing and incremental merge behavior.

Important APIs/functions: constants `dataDirPath`, `dataSymlinkedDirPath`, `dataJSPath`, global `dataDirPaths`, `TestParseYCSB_FromScratch`, and `TestYCSB_Existing`.

Control flow and state: from-scratch tests parse each fixture input root into a temp `data.js` and compare against expected. Existing tests copy raw data, remove 20211027, generate a partial output and confirm it differs, then call `parseYCSB` using the full fixture data and expected `data.js` as the cooked input to verify final output matches.

Dependencies and integration: uses shared mkbench test helpers, temp dirs, and symlinked fixture paths. It validates the backward-compatible parser output format indirectly. Risks not covered include malformed existing JS, multiple cooked files, outlier edge cases, raw parse warnings, and Windows path behavior because tests skip on Windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/ycsb_test.go -->
