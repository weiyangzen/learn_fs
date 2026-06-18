# sources/security-integrity/audit-userspace/lib/flagtab.h

Purpose: Lookup input mapping audit filter list constants to textual names.

Important entries: `task`, `exit`, `user`, `exclude`, `filesystem`, and conditional `io_uring` when `WITH_IO_URING` is configured.

Control flow: Includes `config.h` to see `WITH_IO_URING`; generated into `flagtabs.h`.

State and persistence: Static mapping compiled into translation APIs.

Dependencies and integration: Used by `audit_name_to_flag` and `audit_flag_to_name`, and by rule parsing for filter lists. Conditional `AUDIT_FILTER_URING_EXIT` depends on io_uring support.

Risks: Build-time condition changes accepted rule syntax. Missing io_uring table support while kernel supports it may reject rules.

Test signals: Translation tests with and without `--with-io_uring`; parser tests for `filesystem` and `io_uring` filters.
