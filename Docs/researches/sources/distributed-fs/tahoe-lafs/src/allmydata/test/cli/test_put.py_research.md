# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_put.py

## Purpose
This module tests `tahoe put` for immutable and mutable uploads, stdin and file sources, linked and unlinked destinations, explicit private-key mutable creation, format selection, direct mutable cap updates, Unicode filenames, missing aliases, and leading-slash rejection.

## Important APIs, Types, and Functions
- `Put` combines grid and CLI mixins for command execution.
- `_test_mutable_specified_key` validates `--private-key-path` by deriving mutable keys from an OpenSSL RSA private key and comparing them to the returned cap.
- `_check_mdmf_json`, `_check_sdmf_json`, and `_check_chk_json` validate `ls --json` format and cap families after uploads.
- `test_format` is a matrix over `--mutable`, `--format=SDMF`, `--format=MDMF`, `--format=CHK`, linked destinations, and unlinked uploads.

## Control Flow
Upload tests write local data, run `put`, capture returned caps and stderr status (`200 OK` or `201 Created`), then run `get` or `ls --json` to verify content and metadata. Mutable tests first create caps, then call `put` against the same cap or path and verify in-place replacement returns the same cap. Private-key tests create data files, run `put --mutable --private-key-path`, parse the returned cap, derive expected keys from the PEM file, and fetch the data back.

## State and Persistence Behavior
State includes local data files, grid aliases, linked remote paths, unlinked caps, mutable file contents, and PEM key material in the adjacent test data directory. Mutable operations intentionally preserve capability identity while replacing content. Unicode tests create local non-ASCII filenames and upload them under non-ASCII remote names. The leading slash test checks that a bad remote path does not produce output.

## Dependencies and Integration Points
The module depends on Twisted Trial, `FilePath`, cryptography `load_pem_private_key`, Tahoe RSA key types, `uri.from_string`, `derive_mutable_keys`, `fileutil`, `get_aliases`, CLI option parsing, encoding helpers, and `CLITestMixin`/`GridTestMixin`. It integrates upload behavior with listing and download commands for verification.

## Risks and Edge Cases
Covered risks include stdin status messaging, deterministic LIT/CHK caps for small immutable data, path variants (`./`, absolute, dircap `:./`), mutable in-place updates, explicit private key compatibility, invalid format rejection, MDMF cap extension handling, nonexistent alias errors, Unicode encoding, and rejecting remote paths beginning with `/`.

## Test Signals
The module gives strong format and capability-family signals through JSON checks and direct cap parsing. Content round-trips catch data-path regressions. Some tests assert substrings in stderr rather than full responses, but that keeps the suite less brittle around status wording.
