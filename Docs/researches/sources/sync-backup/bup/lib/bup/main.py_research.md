<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/main.py -->
# sources/sync-backup/bup/lib/bup/main.py

## Purpose
This is the top-level `bup` command dispatcher. It parses global options, adjusts environment, loads built-in command modules, falls back to `bup-*` executables, manages profiling/debug flags, and normalizes process exit behavior.

## Important APIs, Types, And Functions
Important functions are `maybe_import_early()`, `usage()`, `misuse()`, `extract_argval()`, `parse_global_opts()`, `run_subcmd()`, and `main()`.

## Control Flow
At import, it adjusts `PYTHONPATH` from `bup_main.env_pythonpath` and processes early `--import-py-module`. `main()` installs the Ctrl-C handler, parses globals, sets absolute `BUP_DIR`, imports `bup.cmd.<subcmd>`, or locates an external `bup-<subcmd>` executable. `run_subcmd()` updates `BUP_FORCE_TTY`, invokes module `main(args)` or `os.execvp()`, clears progress output, and closes cached catpipes.

## State And Persistence Behavior
It mutates process environment (`PYTHONPATH`, `BUP_DEBUG`, `BUP_FORCE_TTY`, `BUP_DIR`) and uses global logging/progress state. It does not persist repository data directly; subcommands own that work.

## Dependencies And Integration Points
It integrates with `bup.cmd` modules, executable command directory from `bup.path`, `compat.get_argvb()`, `helpers.die_if_errors()`, and `git.close_catpipes()`. It is the user entry point for all bup commands.

## Risks And Edge Cases
Unknown module imports must distinguish missing command modules from import failures inside a command. `--import-py-module` is handled both early and skipped during global parsing. `os.execvp()` replaces the process for external commands, so cleanup only applies to in-process module commands. Environment changes can influence child behavior.

## Test Signals
`test/ext/test-main`, `test/ext/test-help`, `test/ext/test-versioning-and-archive`, command-specific tests, and error-path tests validate usage output, unknown commands, `--help` rewriting, debug/profile flags, and environment propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/main.py -->
