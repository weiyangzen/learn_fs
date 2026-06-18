<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py

Purpose: integration tests for `borg list` on archives, validating formatter fields, JSON-lines output, depth filtering, hardlink inode reporting, chunk counts, hashes, sizes, and content fingerprints.

Important APIs: `cmd`, `create_regular_file`, `requires_hardlinks`, `generate_archiver_tests`, `RK_ENCRYPTION`, JSON parsing, and archive `info --json` for expected archive IDs.

Control flow: each test creates a repository and archive, then invokes `list` with formatting flags. `test_list_hash`, `test_list_chunk_counts`, and `test_list_size` build specific files to check `{sha256}`, `{num_chunks}`, and `{size}`. `test_list_json` and `test_list_json_lines_includes_archive_keys_in_format` parse one JSON object per item. `test_list_depth` builds nested directories and asserts inclusion/exclusion for `--depth=0..3`. Hardlink and fingerprint tests compare formatter results across hardlinked files, changed content, and altered chunker parameters.

State and persistence: archives persist test input trees; temporary large files are removed after archive creation to save space. Fingerprint tests create multiple archives in one repository and rely on chunker-condition changes changing fingerprints.

Dependencies/integration: depends on item formatter fields, archive metadata formatting, chunker behavior, hardlink platform support, and JSON-lines schema. Risks include platform inode absence, exact SHA-256 fixtures, and depth semantics around directories versus files. Test signals are parsed formatter rows, JSON keys, hardlink inode equality, and fingerprint stability/change assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py -->
