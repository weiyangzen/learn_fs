# File Research: sources/os/plan9/9front/sys/src/cmd/sam/error.c

`error.c` maps `Err` and `Warn` enum values to user-facing sam diagnostics and provides formatted error/warning helpers.

Fatal editor errors call `hiccough`, which unwinds the current command, rolls back in-progress edits, updates the terminal, and longjmps back to the main command loop. Variants include plain enum errors, string-argument errors, rune-command errors, and system-error-enhanced errors.

Warnings print to the command/terminal output through `dprint` and do not unwind command execution.

`termwrite` is the common output path. In downloaded mode it inserts text into the command file buffer and advances `cmdptadv`; otherwise it writes directly to fd 2. This keeps diagnostics visible in `samterm`'s command window.
