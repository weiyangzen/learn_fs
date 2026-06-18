# sources/sync-backup/casync/test/report-holes.py

Purpose: diagnostic helper for reporting sparse-file holes/extents.

Important APIs/types/functions: Python script uses seek-style filesystem APIs to walk data/hole regions and print a compact report for a file.

Control flow/state: reads file metadata without mutating it. Output depends on filesystem support for sparse extent reporting.

Dependencies/integration: useful with tests around `loop_write_with_holes`, archive extraction, and sparse file preservation.

Risks/test signals: not portable to filesystems or platforms lacking `SEEK_DATA`/`SEEK_HOLE`. Best used as a manual or conditional diagnostic rather than a strict universal test.

Source research group: `subset-b-009122`.
