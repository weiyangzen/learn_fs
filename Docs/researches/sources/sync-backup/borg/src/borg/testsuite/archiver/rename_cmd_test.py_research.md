<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py

Purpose: verifies `borg rename` updates archive names while preserving archive accessibility and manifest consistency.

Important APIs: `cmd`, `create_regular_file`, `Repository`, `Manifest.load`, and `Manifest.archives`.

Control flow: creates two archives (`test`, `test.2`), confirms both can be dry-run extracted, renames them to `test.3` and `test.4`, confirms extraction by new names, then loads the manifest directly to assert exactly two archives with the new names exist.

State and persistence: repository manifest archive index is mutated by rename; archive payloads remain extractable.

Dependencies/integration: integrates CLI rename with manifest archive storage and repository loading. Risks include stale old names, duplicate manifest entries, or broken archive references after rename. Test signals are dry-run extraction success and manifest `count`/`exists` checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py -->
