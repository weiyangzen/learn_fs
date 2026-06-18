# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_shell.c

## Summary
Implements `#!` shell-script image activation by rewriting the exec argument buffer to invoke the interpreter with optional interpreter arguments and the script filename.

## Main Responsibilities
- Detects shell scripts by endian-adjusted `#!` magic.
- Prevents recursive script interpretation through `imgp->interpreted`.
- Parses interpreter tokens from the first page until newline, `#`, NUL, or page end.
- Replaces original `argv[0]` with interpreter tokens and appends the original script path.
- Stores the interpreter pathname in `imgp->interpreter_name`.

## Important Behavior
The parser treats spaces and tabs as separators and increments `argc` for each interpreter token. It preserves the existing argument/environment tail by moving it forward in the exec argument buffer, then adjusts `begin_envv`, `endp`, and remaining space.

## Risks
Only the first page is searched. A line that reaches page end returns `ENAMETOOLONG`. The parser's `#` comment termination means interpreter arguments after `#` are ignored.
