# sources/sync-backup/bup/configure

## Purpose
Bash configure script that discovers bup's C compiler, Python build flags, platform headers/functions, readline, libacl, and writes generated configuration files.

## Important APIs, Types, and Functions
Functions include `info`, `die`, `usage`, `find-cmd`, `find-prog`, `try-c-code`, `add-cflag-if-supported`, `find-header`, `summarize`, and trap handler `on-exit`. Outputs are `config/config.h`, `config/config.var/*`, and `config/config.vars`.

## Control Flow
Parses `--with-pylint`, redirects logs to `config.log`, selects `CC`, compiles `hello.c`, probes warning/aliasing/wrap flags, finds `python3.x-config`, obtains embed/non-embed flags, checks headers/mincore/readline/libacl, writes config with `dev/refresh`, and removes generated files on failure.

## State and Persistence Behavior
Successful configuration is represented by `config/config.vars`. Temporary files live under `config/tmp`; failure removes outputs to avoid inconsistent state. `config/config.var` records `bup-python-config` and `with-pylint`.

## Dependencies and Integration Points
Feeds `GNUmakefile` build variables and C preprocessor flags. Depends on compiler, pkg-config, git, Python config scripts, readline/libacl headers/libs, and `dev/refresh`.

## Risks and Test Signals
Risks include shell quoting limitations for flags with spaces, pkg-config/header mismatch, Python embed flag fallback, and feature probes silently disabling capabilities. Signals are generated config files, summarized found features, and clean failure with `config.log`.
