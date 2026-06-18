# sources/test-tools/xfstests-bld/run-fstests/dashboard/dashboard.py

Purpose: Flask dashboard for GCE xfstests results. It mirrors result tarballs from GCS, extracts them, parses JUnit XML, groups results by category/date/config, and provides a simple file browser.

Important functions/classes: `results_header`, `result_summary`, `get_results`, `get_property`, `run_shell_command`, `gs_rsync`, `extract_tarballs`, `setup_dirs`, Flask handlers `/favicon.ico`, `/sync`, `/`, `/files/<path>`, `/files/`, and `testresult`.

Control flow: root handler validates `RESULTS_GS_PATH`, ensures local dirs, triggers sync/extraction, walks extracted results, reads `results.xml`, optionally categorizes LTM watch jobs from nearby `ltm-info/report`, builds an HTML table by category/date/TESTCFG, and links each cell into the file browser. `/sync` runs `gcloud storage rsync` and extraction only when rsync output indicates changes.

State/persistence: local mirror path defaults to `/tmp/mirror`, extracted results to `/tmp/extracted/`; these persist for the container instance lifetime. No database is used.

Dependencies/integration: depends on Flask, junitparser, gcloud CLI, tar, mkdir/rm commands, result tarball layout, JUnit properties including `TESTCFG`, and Cloud credentials.

Risks: command construction uses string concatenation and `split(' ')`, so paths with spaces break. File browser concatenates requested paths under `extracted_dir` without normalization, creating path traversal risk. HTML is unescaped for file contents and metadata. `extract_tarballs` has a likely path check bug by joining `extract_path` twice.

Test signals: unit tests can cover parsing/grouping; integration tests should sync a fixture bucket/local tree, parse known results.xml, and validate file browser containment.
