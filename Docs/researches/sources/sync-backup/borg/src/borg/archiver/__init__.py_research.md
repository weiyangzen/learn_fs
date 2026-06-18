# sources/sync-backup/borg/src/borg/archiver/__init__.py

## Purpose
This module is Borg's top-level CLI orchestrator. It composes command mixins into the `Archiver` class, builds the argument parser hierarchy, parses and normalizes command-line arguments, sets up logging/profiling/signal handling, dispatches commands, handles user-facing exceptions, and provides the `main()` entry point used by console scripts and `borg.__main__`.

## Important APIs, Types, and Functions
- Top-level assertion guard refuses Python optimized mode by requiring working `assert` statements.
- `Archiver` inherits all command mixins, including analyze, benchmark, check, create, extract, repo operations, tar operations, transfer, and version.
- `Archiver.print_warning`, `print_warning_instance`, and `print_file_status` centralize warning/exit-code registration and list/json file-status output.
- `Archiver.CommonOptions` registers common options at multiple parser hierarchy levels with top-level defaults and subparser `SUPPRESS` semantics.
- `build_parser()` constructs the root parser, common parsers, optional `borgfs` parser, and all subcommand parsers by calling each mixin's `build_parser_*`.
- `get_args()` handles normal parsing and SSH forced-command `borg serve` reconciliation, allowing only a small allowlist of client-supplied options to override forced command attributes.
- `parse_args()` preprocesses args, flattens nested namespaces, validates cross-option constraints, applies timestamp-based placeholder overrides, and resolves the function to dispatch.
- `run()` sets umask, logging, progress defaults, selftests, msgpack compatibility checks, optional profiling, and invokes the selected command.
- `sig_info_handler`, `sig_trace_handler`, `format_tb`, and `main()` implement runtime diagnostics and final exception-to-exit-code handling.

## Control Flow
At import time the module imports dependencies in a protective `try` block so import-time crashes exit as Borg errors rather than Python warning rc mismatches. Runtime starts in `main()`, which wraps stdout/stderr for replacement encoding errors, installs signal/fault handlers, constructs `Archiver`, parses args including `SSH_ORIGINAL_COMMAND`, optionally runs the Cockpit TUI, otherwise calls `archiver.run(args)` under the SIGINT helper. `run()` configures logging only after determining whether the command is `serve`, applies implied loggers for options such as `--stats` and `--progress`, warns about unsupported option combinations, runs selftests, checks msgpack implementation, optionally profiles, and dispatches. Exceptions are normalized into Borg exit codes and optionally formatted tracebacks/sysinfo.

## State and Persistence Behavior
This module mutates process-level state: `umask`, stdout/stderr wrappers, logging levels/handlers, signal handlers, debug logger levels, optional profile output files, and process exit code. It does not directly mutate repositories except through dispatched command mixins. It may run selftests and can launch the Cockpit TUI. `get_args()` mutates parsed namespaces for forced-command serve scenarios.

## Dependencies and Integration Points
It integrates with every `archiver/*_cmd.py` mixin, `_common` parser/decorator helpers, Borg helpers/constants/logging, selftests, legacy remote error formatting, platform flags, and optional Cockpit UI. It is the endpoint called by `src/borg/__main__.py` and console entry points. The parser output supplies attributes consumed by `_common.with_repository` and command methods.

## Risks and Edge Cases
- Parser/common-option precedence is subtle; `flatten_namespace()` and `CommonOptions` must preserve the intended "most specific wins" behavior.
- Forced-command `borg serve` security depends on a strict denylist/allowlist and correct parsing of `SSH_ORIGINAL_COMMAND`.
- The top-level import block exits the interpreter on import errors, which is appropriate for CLI but makes library-style import behavior less flexible.
- Signal handlers inspect stack frames and local variable names, so refactors of create/extract internals can break SIGUSR1/SIGINFO diagnostics.
- Profiling writes potentially sensitive execution data to user-specified files.
- `assert rc is None` in `run()` assumes command methods communicate exit status through Borg's global exit-code helpers.

## Test Signals
Tests should cover parser construction for all commands, common-option placement before/after subcommands, placeholder replacement under `--timestamp`, forced `borg serve` allowlist behavior, Cockpit import failure path, logging level implications, unsupported msgpack/pure-Python msgpack warnings, profiling output formats, and exception-to-exit-code mapping. CLI smoke tests should include `borg -h`, `borg help`, `borg --version`, invalid args, and signal behavior where practical.
