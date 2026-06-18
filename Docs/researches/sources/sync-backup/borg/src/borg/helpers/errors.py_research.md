# sources/sync-backup/borg/src/borg/helpers/errors.py

## Purpose
Defines Borg's structured error and warning classes with modern/legacy exit-code behavior and backup-specific wrappers.

## Important APIs, Types, And Functions
`ErrorBase`, `Error`, `ErrorWithTraceback`, `IntegrityError`, `DecompressionError`, `CancelledByUser`, `RTError`, `CommandError`, and `PathNotAllowed` are raised errors. `BorgWarning`, `FileChangedWarning`, `IncludePatternNeverMatchedWarning`, `BackupWarning`, `BackupError`, `BackupRaceConditionError`, `BackupOSError`, `BackupPermissionError`, `BackupIOError`, `BackupFileNotFoundError`, and `BackupItemExcluded` model warnings, backup access failures, and internal skipping.

## Control Flow
Message text is taken from class docstrings and formatted with constructor args. `exit_code` properties return class-specific modern codes when `BORG_EXIT_CODES=modern` at import time, otherwise generic legacy warning/error codes. `BackupWarning.exit_code` delegates to the wrapped `BackupError` in modern mode.

## State And Persistence
The only module state is `modern_ec`, derived once from the environment at import. Error instances retain args and, for `BackupOSError`, selected `OSError` fields.

## Dependencies And Integration Points
Uses constants for exit-code ranges and low-level crypto `IntegrityError` as a base for integrity failures. These classes are consumed by archiver top-level exception handling, backup traversal, repository integrity checks, and helpers warning aggregation.

## Risks And Edge Cases
Docstring formatting means constructor arg counts must match class docs. `modern_ec` does not react to environment changes after import. `BackupWarning` asserts its second arg is a `BackupError`, which can fail loudly if misused. `BackupItemExcluded` is intentionally not an `ErrorBase`.

## Test Signals
Tests should cover formatted messages, modern/legacy exit code switching in isolated processes or module reloads, traceback flags, `BackupOSError` field copying, and `BackupWarning` exit code delegation.
