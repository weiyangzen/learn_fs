<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py

Purpose: integration and regression tests for `borg transfer`, especially Borg 1-to-2 migration, archive metadata preservation, recompression, rechunking, dry-run safety, and source index immutability.

Important APIs: `setup_repos`, `cmd`, `open_archive`, `open_item`, `parse_timestamp`, `parse_file_size`, `ChunkerParams`, Borg 1 `repo12.tar.gz`, JSON/tarfile/stat/hashlib helpers, and environment passphrases `BORG_PASSPHRASE`/`BORG_OTHER_PASSPHRASE`.

Control flow: Borg 1 tests extract fixture repos, create a Borg 2 destination with `--from-borg1`, transfer, compare repo-list and item JSON after normalizing expected schema differences, and inspect stored items directly. SSH legacy transfer uses `ssh://__testsuite__`. Normal transfer uses `setup_repos` to switch archiver from source repo to destination repo. Metadata, recompression, and rechunking tests compare archive JSON, compact-reported repository sizes, chunker params, expected fixed chunk counts, and SHA-256 of item contents. Dry-run ensures rechunking path does not create archives. Issue #9022 records source Borg 1 index metadata before/after transfer.

State and persistence: switches `archiver.repository_location`/`repository_path`, creates two repos with different passphrases, transfers archives, reads direct archive objects, and inspects legacy index files.

Dependencies/integration: depends on local-only legacy fixtures for Borg 1 cases, repository compatibility layers, compression/chunker implementations, JSON schema, and platform differences for block devices on Windows. Risks include fixture drift, source repo mutation, metadata normalization gaps, and memory size assumptions while reading item contents. Test signals are repo checks, JSON equality after normalization, archive metadata equality, repository size comparisons, chunk counts, content hashes, and unchanged index metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py -->
