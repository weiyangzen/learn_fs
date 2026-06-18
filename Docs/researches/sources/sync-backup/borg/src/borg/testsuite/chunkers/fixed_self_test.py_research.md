<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py

Purpose: Borg self-test coverage for `ChunkerFixed`.

Important APIs: `ChunkerFixed`, `BaseTestCase`, `cf`, `BytesIO`, and allocation constants.

Control flow: tests fixed block splitting with and without header size; then repeats with explicit file maps. Complete maps should emit all expected blocks, maps marking zero regions as holes should produce integer hole lengths, and partial maps should only emit mapped data ranges.

State and persistence: in-memory `BytesIO` only.

Dependencies/integration: self-test must avoid pytest and stay aligned with self-test counts. Risks include header offset arithmetic, file-map partial coverage, and hole/data metadata consistency. Test signals are exact normalized chunk lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py -->
