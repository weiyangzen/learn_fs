# File Research: sources/os/linux/linux-stable/fs/binfmt_script.c

## Summary
Implements the kernel `#!` script binary loader. It parses the first line of a script, prepares interpreter arguments, and restarts exec with the interpreter file.

## Main Responsibilities
- Detects scripts whose first two bytes are `#!`.
- Parses interpreter path and optional single argument from `bprm->buf`.
- Rejects truncated interpreter paths.
- Replaces original `argv[0]` with script filename and interpreter argv.
- Opens the interpreter with `open_exec()`.
- Registers and unregisters the script `linux_binfmt`.

## Important Behavior
The parser does not assume `bprm->buf` is NUL-terminated. If no newline is present, it requires a terminator after the interpreter path so the path is not silently truncated. Truncated interpreter arguments are tolerated because interpreters can re-read the script.

The argument stack is rebuilt in reverse order: script path, optional interpreter argument, interpreter name. `bprm_change_interp()` records the interpreter path before `open_exec()` installs the interpreter file.

## Risks
The path-inaccessible check rejects `/dev/fd`-style scripts that would disappear after exec. Correct shebang parsing depends on distinguishing interpreter path truncation from argument truncation.
