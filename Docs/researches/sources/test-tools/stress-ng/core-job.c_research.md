# sources/test-tools/stress-ng/core-job.c

## Purpose

This file parses stress-ng job files into ordinary stress-ng option arguments. Job files can also specify whether contained jobs should run sequentially or in parallel.

## Important APIs, Types, And Functions

`MAX_ARGS` limits parsed tokens per line. `RUN_SEQUENTIAL` and `RUN_PARALLEL` track mutually exclusive job run modes. Internal helpers are `stress_str_chop`, `stress_parse_run`, and `stress_parse_error`. The public API is `stress_job_parse_file`.

## Control Flow

`stress_job_parse_file` opens an explicit jobfile or consumes `argv[optind]`, uses `setjmp(g_error_env)` to catch option parser failures, reads lines, removes newline and comments, tokenizes on blanks, rejects recursive `job` commands, handles `run sequential|seq|sequentially` and `run parallel|par|together`, prefixes the command token with `--`, and calls `stress_opts_parse` in job mode. It returns zero on success and `-1` on parse/open errors.

## State And Persistence Behavior

The parser mutates global option flags for sequential/parallel mode and advances `optind` when consuming an implicit jobfile. It allocates a temporary `--option` string per parsed line and frees it immediately. Parsed options persist through the global stress-ng settings system.

## Dependencies And Integration Points

It depends on global `g_error_env`, `g_opt_flags`, `OPT_FLAGS_SEQUENTIAL`, `OPT_FLAGS_ALL`, `stress_opts_parse`, and libc file/token APIs. It integrates with command-line parsing before stressor execution.

## Risks And Test Signals

The tokenizer does not implement quoting, so paths or arguments containing spaces are not supported. Invalid job recursion and conflicting run modes must remain guarded. Test signals include comments and blank lines, implicit and explicit file opening, sequential/parallel mode toggles, invalid options through `setjmp`, out-of-memory handling, and line-numbered diagnostics.
