# sources/storage-engines/foundationdb/contrib/TestHarness2/analyze_determinism_failure.py

Purpose: standalone diagnostic tool comparing trace JSON from an initial simulation run and its determinism-check rerun to find divergence, especially around S3 and bulk dump events.

Important APIs/functions: `parse_trace_file`, `extract_key_events`, `normalize_event`, `compare_event_sequences`, `extract_s3_operations`, `analyze_s3_operations`, `compare_early_events`, `find_divergence_point`, `analyze_duplication_pattern`, and `main`.

Control flow: CLI takes two directories, loads all `*.json` traces from each, compares early event types and selected fields, locates the first divergence, detects approximate 2x duplication patterns, extracts key event types, compares S3 filenames, and prints a summary.

State and persistence: read-only; no output files. All state is in lists/dicts of parsed JSON events.

Dependencies and integration: Python stdlib only. `run.py` writes a README command pointing users at this script when determinism analysis directories are created.

Risks and test signals: assumes JSON line traces and directory-level glob ordering; comparisons are event-order sensitive and normalize only known timing fields. Test with synthetic traces covering count mismatch, first type mismatch, S3 object mismatch, malformed JSON, and missing files.
