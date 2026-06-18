<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py

Purpose: verifies warning/error exit code behavior in classic and modern modes.

Important APIs: `cmd`, `changedir`, `IncludePatternNeverMatchedWarning`, `Repository.DoesNotExist.exit_mcode`, `EXIT_ERROR`, and `BORG_EXIT_CODES`.

Control flow: `test_return_codes` creates and extracts an archive, then extracts with a non-matching include path under forked execution and expects the include-pattern warning exit code. `test_exit_codes` creates an uninitialized repo directory, runs `create` under `BORG_EXIT_CODES=classic` expecting generic `EXIT_ERROR`, then under `modern` expecting the specific repository-does-not-exist machine code.

State and persistence: manipulates repository directory existence without initialization and changes process environment for exit-code mode.

Dependencies/integration: depends on forked command execution and modern error code mapping. Risks include environment leakage and error taxonomy changes. Test signals are exact expected exit codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py -->
