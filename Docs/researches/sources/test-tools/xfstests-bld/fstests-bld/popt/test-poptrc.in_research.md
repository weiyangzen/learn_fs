# sources/test-tools/xfstests-bld/fstests-bld/popt/test-poptrc.in

Purpose: popt configuration fixture for `test1`. It defines aliases and exec entries used by the shell test harness to validate config-file parsing, alias expansion, argument substitution, and help metadata.

Important entries: aliases for `--simple`, `--two`, `--takerest`, `-T`, `-O`, `--grab`, `--grabbar`, and `-e`; exec entries for `--echo-args` and `-a` mapped to `/bin/echo`; `--POPTdesc` and `--POPTargs` metadata make `--simple` visible in help.

Control flow/state: when read by `poptReadConfigFile`, matching lines for app `test1` become `con->aliases` or `con->execs`. Aliases are later expanded by `handleAlias`; execs are deferred until parser completion by `handleExec`/`execCommand`.

Dependencies/integration: consumed by `test1.c` and `testit.sh`; requires parser support for quote handling and `!#:+` next-argument substitution.

Risks: because exec entries can run external commands, production config files require trusted locations and sane permissions. The fixture uses shell-style quoted strings that depend on `poptParseArgvString` behavior.

Test signals: most alias and exec cases in `testit.sh` depend on this file, including `--simple`, `--two`, `--takerest`, `--grab`, and `--echo-args`.
