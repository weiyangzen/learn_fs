# File Research: sources/local-fs/ocfs2-tools/libtools-internal/verbose.c

Implements shared verbose/error/interactive output behavior for ocfs2-tools.

Key responsibilities:
- Tracks program basename, verbosity level, and interactive mode.
- Wraps normal output so active progress displays are cleared and restored.
- Can suppress `com_err()` output when quiet mode drives verbosity below normal.
- Provides yes/no prompting with optional preset answers.
- Prints tool version using compiled `VERSION`.

Important functions:
- `tools_setup_argv0()`, `tools_progname()`.
- `tools_verbose()`, `tools_quiet()`, `tools_verbosity()`.
- `verbosef()`, `errorf()`, `tcom_err()`.
- `tools_interactive()`, `tools_interactive_yes()`, `tools_interactive_no()`, `tools_interact()`, `tools_interact_critical()`.
- `tools_version()`.

Dependencies:
- `com_err` hooks.
- `tools-internal/progress.h` and private `libtools-internal.h`.

Research notes:
- `tools_interact()` auto-approves if interactive mode is disabled.
- `tools_interact_critical()` always asks, intended for high-risk confirmations.
- Output target can be switched to stdout via `VL_FLAG_STDOUT`.
