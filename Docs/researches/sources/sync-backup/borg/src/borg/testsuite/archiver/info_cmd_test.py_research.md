# sources/sync-backup/borg/src/borg/testsuite/archiver/info_cmd_test.py

Purpose: tests `borg info` archive and repository output, JSON schema for archive metadata, empty archive selection behavior, and recorded working directory metadata.

Important APIs/types/functions: `test_info`, `test_info_json`, `test_info_json_of_empty_archive`, and `test_info_working_directory` use `cmd`, `create_regular_file`, `checkts`, `changedir`, JSON decoding, and `RK_ENCRYPTION`.

Control flow: basic info creates one archive and checks text output for `Archive name: test`, including selection by `--first 1`. JSON info decodes `info -a test --json`, asserts a single archive, validates name, command line type, duration, 64-character ID, empty tags, stats presence, and ISO-like start/end timestamps via `checkts`. Empty repo JSON with `--first`/`--last` must return an empty archives list. Working-directory test creates an archive from inside the input directory and asserts text info records that absolute cwd.

State and persistence behavior: creates repositories, archives, and input files. Working-directory metadata is persisted in archive metadata and later rendered by info.

Dependencies and integration points: covers info command, archive selection filters, archive metadata serialization, timestamp formatting, and creation metadata.

Risks: output string expectations depend on text formatting. JSON schema changes for archive metadata must keep these keys or update tests.

Test signals: confirms both human and machine-readable info output expose core archive metadata and handle empty selections cleanly.
