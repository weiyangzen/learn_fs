# sources/test-tools/xfstests-bld/fstests-bld/popt/test2.c

Purpose: "real world" popt test program modeling a create-user style command with grouped option tables for transaction, database, and user fields. It checks nested include tables and config-file defaults.

Important state/APIs: global string and integer fields represent command options. `userOptionsTable`, `transactOptionsTable`, and `databaseOptionsTable` are included into `optionsTable`, which also includes `POPT_AUTOHELP`. Main calls `poptGetContext`, `poptReadConfigFile(rcfile)`, one `poptGetNextOpt`, and `poptFreeContext`.

Control flow: before parsing, include table `arg` pointers are filled at runtime. The rcfile defaults are read before parsing command-line options. The program calls `poptGetNextOpt` primarily to service `--help`, then prints all collected config/option values.

State/persistence: option values are global pointers updated by popt string parsing or config defaults. The parser context owns only its internal allocations; target strings assigned by `POPT_ARG_STRING` are duplicated and not explicitly freed by this program.

Dependencies/integration: depends on `system.h`/popt APIs and a `createuser-defaults` config file if used.

Risks: parsing only one option means it is not a general complete parser for all command-line options; it is intended as a bug reproducer/help/config test. Printed `%s` with NULL pointers may emit `(null)` on glibc but is not fully portable.

Test signals: useful for include-table help/config regressions, but it is not wired into the visible `testit.sh` active cases.
