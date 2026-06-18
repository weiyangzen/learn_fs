# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/verbose.h

## Purpose

Declares internal verbosity, error output, version output, and interactive prompt APIs.

## Main Contents

- Verbosity levels for critical, error/output, application status, library status, and debug messages.
- `VL_FLAG_STDOUT` and `VL_OUT` to direct ordinary output to stdout.
- Program identity/version setup: `tools_setup_argv0()`, `tools_progname()`, and `tools_version()`.
- Verbosity and interactivity controls: `tools_verbose()`, `tools_quiet()`, `tools_interactive()`, `tools_interactive_yes()`, and `tools_interactive_no()`.
- Formatted output functions: `verbosef()`, `errorf()`, `tcom_err()`, `tools_interact()`, and `tools_interact_critical()`, all with printf-format checking.

## Dependencies and Integration

- Uses `errcode_t` for com_err-style errors, so including code must have error table types visible.
- Coordinates with progress display code according to comments in `progress.h`.
