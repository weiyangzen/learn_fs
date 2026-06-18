# sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.h

Purpose: public declarations and core command-construction logic for native `fdbmonitor`. It defines logging severities, platform fd abstractions, utility declarations, environment parsing helpers, and the `Command` type that translates ini sections into process argv and restart policy.

Important APIs and types: `Severity`, `ProcessID`, utility declarations (`timer`, `parseWithSuffix`, path helpers, `load_conf`, `kill_process`, etc.), `EnvVarUtils`, and `Command`. `Command` owns `argv`, stdout/stderr pipes, restart-delay fields, envvar strings, deconfiguration state, `kill_on_configuration_change`, and memory RSS limit.

Control flow: the `Command` constructor merges keys from process section, process-id subsection, and `general`; resolves restart settings; parses envvars/delete-envvars; reads `command`; configures memory limits; builds argv from the command string plus ini keys. It expands `$ID` and `$PID`, handles `flag_`/`flag-` boolean flags, and excludes monitor-only keys from child argv.

State and persistence behavior: each `Command` creates monitored pipes and owns duplicated argv strings. Destruction unmonitors and closes pipes. `update` carries forward mutable restart state while applying new policy values. `get_and_update_current_restart_delay` resets after a quiet interval, adds jitter, and backs off.

Dependencies and integration points: uses `SimpleIni`, POSIX pipes/fd watching, Linux memory defaults, and functions implemented in `fdbmonitor_lib.cpp`. Instances are stored in global maps and driven by `load_conf` and `start_process`.

Risks: command tokenization uses whitespace splitting, so quoted command arguments are not preserved. Invalid config often logs and returns from the constructor with `argv` possibly unset. Environment variable syntax permits exactly one equals sign, which excludes some values.

Test signals: `fdbmonitor_tests.cpp` covers `EnvVarUtils`; path helpers are declared here but implemented/tested in the library.
