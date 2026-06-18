<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go

This file tests `WalkCompare`. It builds temp directory scenarios for identical data, content changes, deletions, permission/time-like differences, directory/root rename filtering, report validation, and rerooting behavior.

The tests exercise both success paths and failure-report behavior, including custom global filters. They rely on real filesystem mutations and fswalker report structures.

Risks covered include false positives from expected metadata drift and false negatives from invalid reports. Residual risk remains around large files, platform-specific UID/GID/time behavior, and hashing limits. These are key signals for snapshot restore correctness checks in robustness tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go -->
