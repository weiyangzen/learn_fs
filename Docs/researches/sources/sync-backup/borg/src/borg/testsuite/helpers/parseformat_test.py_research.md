# sources/sync-backup/borg/src/borg/testsuite/helpers/parseformat_test.py

Purpose: comprehensive tests for parse/format helpers: binary/text JSON encoding, repository locations, archive/text validators, time intervals, timestamps, file sizes, placeholder formatting, display-width slicing, escape evaluation, and chunker parameter parsing.

Important APIs and control flow: early tests cover `bin_to_hex`, `binary_to_json`, and `text_to_json` including surrogateescape fallback with `_b64` fields. `TestLocationWithoutEnv` removes `BORG_REPO` and verifies `Location` parsing/canonicalization for ssh/rest IPv4/IPv6 forms, file paths, s3/b2/rclone/sftp/http passthrough with credential stripping, local absolute/relative paths, SMB-style paths, colons, canonical idempotence, and bad syntax. Validators reject invalid archive names, control characters, NULs, surrogate escapes, and length violations. Formatting tests cover `format_timedelta`, `interval`, `parse_timestamp`, SI/IEC file-size formatting, parsing file-size suffixes, `partial_format`, `clean_lines`, `format_line`, placeholder errors, `replace_placeholders`, `swidth_slice`, `eval_escapes`, and `ChunkerParams` for buzhash/fixed modes and invalid boundaries.

State and persistence: mostly pure parsing. It mutates environment variables, uses current time for `{now}`, and conditionally skips display-width tests depending on platform `swidth`.

Dependencies and integration points: depends on constants, `helpers.argparsing.ArgumentTypeError`, `helpers.parseformat`, `helpers.time`, and platform flags. These helpers integrate with CLI argument parsing, repository location identity/security, archive naming, output formatting, and chunker configuration.

Risks: location parsing is security-sensitive because credentials must be stripped from canonical paths while raw processed URLs remain usable. Placeholder formatting guards against attribute traversal. Chunker parameter validation must prevent unsupported memory/object sizes.

Test signals: exact `repr(Location)`, canonical path idempotence, expected exceptions, file-size strings, placeholder outputs, escape results, and chunker tuple values.
