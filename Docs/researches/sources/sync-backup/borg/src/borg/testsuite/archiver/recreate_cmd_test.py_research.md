<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py

Purpose: integration coverage for `borg recreate`, including exclusion modes, subtree selection, hardlinks, rechunking, timestamps, comments, dry-run, list output, target archive creation, and protected archive handling.

Important APIs: `cmd`, `create_test_files`, `create_regular_file`, cache/tag helper setup/assertions, `_extract_hardlinks_setup`, `changedir`, and hardlink capability checks.

Control flow: tests first create archives with controlled input, then call `recreate` with filters such as `--exclude-caches`, `--exclude-if-present`, `--keep-exclude-tags`, explicit paths, excludes, `--target`, `--chunker-params`, `--timestamp`, `--comment`, `--list`, and `--info`. Follow-up commands run `check`, `list`, `extract`, or `info` to verify archive contents and metadata. Hardlink tests assert recreated subtrees preserve link counts.

State and persistence: `recreate` rewrites archive metadata and item streams unless dry-run or target mode is used. It may preserve original archive IDs when no work is needed, preserve nominal timestamps, or create new archive names.

Dependencies/integration: depends on archive item filtering, files cache/tag helpers, chunker parameter parsing, hardlink restoration, local timezone formatting, and protected tag semantics. Risks include unintended rechunking, losing comments/timestamps, deleting protected archives, or mishandling hardlinked exclude tags. Test signals are archive listings, chunk counts, `info` text, repository checks, and output inclusion/exclusion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py -->
