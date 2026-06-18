# sources/test-tools/crashmonkey/code/results/FileSystemTestResult.h

Purpose: declares filesystem-level result state and error vocabulary.

Important APIs/types: `ErrorType` covers check-not-run, clean, unmountable, check error, fixed, snapshot restore, bio write, other, kernel mount failure, and unfixed fsck errors. Public strings store an error description and raw fsck output.

Control flow and integration: `FsSpecific` returns `ErrorType` values from checker exit codes; `Tester` sets errors based on replay/mount/fsck outcomes; result printers consume the state.

State: private unsigned bitmask `error_summary_`, plus public description/output strings for logs.

Risks: anonymous namespace constants in a header, exact-equality assumptions elsewhere, and bitmask combinations that can include `kClean` alongside failures.

Test signals: result classification in `SingleTestInfo` is the key downstream behavior to validate.
