# sources/test-tools/lcov/bin/gendesc

Purpose: lcov command-line tool that converts a human-readable test description file into the `TN:` and `TD:` description format consumed by `genhtml`.

Important APIs/types/functions: Perl modules `File::Basename`, `Getopt::Long`, `Cwd::abs_path`, `FindBin`, and `lcovutil`; imported globals `$tool_name`, `$tool_dir`, `$lcov_version`, `$lcov_url`, `die_handler`, and `warn_handler`; options `--output-filename`, `--version`, and `--help`; functions `print_usage` and `gen_desc`.

Control flow: the script installs lcovutil warning/die handlers, parses options, handles help/version exits, requires one input filename, and calls `gen_desc`. `gen_desc` opens the input and optional output file, then scans line by line. A line matching `^(\w[\w-]*)(\s*)$` starts a test name and emits `TN: name`. An indented nonblank line emits `TD: text`. Empty lines inside observed description blocks are preserved as a single `TD: ` paragraph separator when followed by another description line.

State/persistence behavior: output is written to stdout unless `--output-filename` is provided, in which case the target file is overwritten. No other persistent state is maintained.

Dependencies/integration: installed as one of the public lcov executables. It depends on `lib/lcovutil.pm` for tool metadata and shared diagnostics, and its output is consumed by `genhtml` as test-case description metadata.

Risks/test signals: malformed lines are silently ignored rather than rejected, so input mistakes can drop descriptions without a nonzero exit. Test names are limited to word characters plus hyphen after a word-character start. The script imports some modules/globals that are not directly used after initialization. Signals are help/version output, conversion of multi-line descriptions, preservation of paragraph breaks, and correct file overwrite behavior with `-o`.
