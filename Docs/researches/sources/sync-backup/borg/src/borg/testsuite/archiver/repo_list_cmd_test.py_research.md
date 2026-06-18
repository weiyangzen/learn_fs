<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py

Purpose: integration tests for `borg repo-list`, covering archive matching, custom formats, archive sizes/file counts, date filters, JSON schema, deleted archive visibility, and Borg 1 listing compatibility.

Important APIs: `cmd`, `checkts`, `create_regular_file`, `_create_archive_ts`, JSON, and Borg 1 testdata tarball.

Control flow: tests create archives with names, comments, sizes, and timestamps, then run `repo-list` with `--match-archives`, default/custom formats, `--short`, date filters (`--oldest`, `--newest`, `--newer`, `--older` with multiple units), `--json`, `--deleted`, and `--from-borg1`. The Borg 1 test extracts `repo12.tar.gz`, sets passphrase/KDF env, and points the archiver at that repository.

State and persistence: repository archive index is populated, logical deletion hides archives from normal listings, and Borg 1 fixture repositories are read locally.

Dependencies/integration: depends on archive formatter, date interval parsing, deletion semantics, JSON metadata, and legacy repository reader. Risks include time-relative tests becoming brittle, short output length assumptions, and Borg 1 environment requirements. Test signals are string membership, parsed JSON fields, timestamp validation, and expected exit code for invalid interval.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py -->
