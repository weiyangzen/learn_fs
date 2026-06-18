# sources/sync-backup/borg/src/borg/archiver/check_cmd.py

## Purpose
This module implements `borg check`, the command that verifies repository-level consistency and archive-level metadata/data consistency. It wires CLI validation, repair confirmation, repository checks, archive checks, and parser help/options around the `Repository.check()` and `ArchiveChecker` implementations.

## Important APIs, Types, and Functions
- `CheckMixIn.do_check(args, repository)` is decorated with `with_repository(exclusive=True, manifest=False)`, so it opens the repository exclusively but defers manifest/key handling to check logic.
- `yes(...)` confirmation with `BORG_CHECK_I_KNOW_WHAT_I_AM_DOING` environment override gates `--repair`.
- Cross-option validation rejects contradictions: `--repository-only` with archive filters or `--verify-data`, `--repository-only` with `--find-lost-archives`, `--repair` with `--max-duration`, and `--max-duration` without `--repository-only`.
- It pre-fetches the archive key from the manifest when archive checks will run, so passphrase prompting happens before lengthy repository checks.
- `repository.check(repair=args.repair, max_duration=args.max_duration)` performs low-level repository verification.
- `ArchiveChecker.check(...)` performs archive metadata/chunk verification, optional data verification, repair, lost archive recovery, and archive filter handling.
- `build_parser_check()` registers check options and shared archive filters with a detailed epilog.

## Control Flow
The command opens the repository with an exclusive lock. If repair is requested, it prompts for an exact `YES` unless overridden by environment. It validates incompatible option combinations. If archive checks are needed, it instantiates `ArchiveChecker` and attempts `make_key(..., manifest_only=True)` early. It runs repository checks unless `--archives-only` is set; failures set Borg's warning exit code. It then runs archive checks unless `--repository-only` is set; archive-check failure also sets the warning exit code.

## State and Persistence Behavior
Without `--repair`, the command is intended to be read-only, though repository partial-check bookkeeping may be internal to `Repository.check()`. With `--repair`, it can delete corrupt repository objects, rebuild or write manifests, recreate lost archive-directory entries, remove broken archive entries, and delete chunk-index caches through `ArchiveChecker`. `--max-duration` enables partial repository checks only and cannot be combined with archive checks or repair.

## Dependencies and Integration Points
It depends on `_common.with_repository`, `_common.Highlander`, `ArchiveChecker`, constants, helper exit-code and prompt classes/functions, and shared archive filter parser helpers. It delegates most deep behavior to `Repository.check()` and `archive.py`'s `ArchiveChecker`. The parser's archive filter options must stay aligned with `ArchiveChecker.check()` parameters.

## Risks and Edge Cases
- `--repair` is explicitly dangerous and can cause data loss when corruption is not fully recoverable.
- Partial checks are non-cryptographic repository checks only; users may overestimate their coverage.
- Early key prompting improves UX but falls back silently if manifest-only key creation fails; archive checking later tries again.
- The command uses warning exit codes for detected issues, so automation must interpret Borg's modern/legacy exit code semantics correctly.
- Archive filters with check can leave unselected archives unchecked; this is useful but can surprise users expecting full repository validation.

## Test Signals
Tests should cover option contradiction errors, repair confirmation and environment override, repository-only/archive-only branching, partial check requirements, archive filter forwarding, warning exit-code setting, and passphrase/key-prompt ordering. Integration tests should use repositories with missing chunks, corrupt archive metadata, corrupt data objects, missing manifests, and lost archive entries, with and without repair.
