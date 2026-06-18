# sources/sync-backup/git-lfs/t/t-pointer.sh

Purpose: command-line coverage for `git lfs pointer`, including pointer generation, pointer parsing, comparison, strict validation, stdout/stderr routing, and extension-aware pointer generation.

Important APIs/functions: uses `git lfs pointer` flags `--file`, `--stdin`, `--pointer`, `--check`, `--strict`, `--no-strict`, `--compare`, and `--no-extensions`; helper functions include `is_stdin_attached`, `setup_case_inverter_extension`, `calc_oid`, `invert_case`, and `$LFSTEST_EXT_LOG`.

Control flow: early tests compare generated pointer text for file input and STDIN, including match/mismatch cases and missing or malformed pointer files. Validation tests run `--check` against valid pointers, invalid text, empty files, zero-size pointers, CRLF pointers, and invalid flag combinations. Output-routing tests ensure pointer payload goes to stdout while labels go to stderr when redirected. Extension tests configure a case-inverter extension, confirm warning and `ext-0-caseinverter` lines, compare extension versus no-extension pointers, and verify extension clean invocations across multiple files.

State/persistence behavior: most tests create temporary files in fresh repos and compare deterministic SHA-256 OIDs, Git blob OIDs, status codes, and extension logs. Extension cases persist `.gitattributes` and extension configuration, and then check whether transformation logs were or were not written.

Dependencies/integration points: integrates pointer parser/serializer code, Git blob hashing, LFS extension clean filters, terminal/stdin detection, CRLF tolerance, and command validation.

Risks/test signals: regressions include invalid pointers accepted, valid pointers rejected, wrong exit status, broken stream separation, incorrect extension OIDs, or missing mismatch diagnostics. Exact output expectations make this suite sensitive to wording and formatting changes.
