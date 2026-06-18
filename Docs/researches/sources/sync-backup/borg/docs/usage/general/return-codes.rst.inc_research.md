# sources/sync-backup/borg/docs/usage/general/return-codes.rst.inc

Purpose: documents Borg process return-code semantics.

Important APIs and control flow: rc `0` means success, `1` generic warning, `2` generic error, `3..99` specific errors, `100..127` specific warnings, and `128+N` signal termination. Specific codes require modern exit-code mode; `--show-rc` logs the return code as the last log entry.

State and persistence: no persistent state; process exit status and optional final log line are automation contracts.

Dependencies and integration points: `BORG_EXIT_CODES`, logging levels, message IDs, shell/systemd automation, and monitoring.

Risks: legacy mode collapses all warnings/errors to 1/2, so scripts expecting specific codes must ensure modern mode. Warnings may still complete the operation.

Test signals: command fixtures producing success, warning, generic error, specific errors/warnings, signal termination mapping, and `--show-rc` final log emission.
