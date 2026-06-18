<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/chdir.c -->
## sources/test-tools/strace/src/chdir.c

Purpose: Decodes the single-argument `chdir` syscall.

Important APIs and types: `SYS_FUNC(chdir)`.

Control flow: Prints argument name `path`, calls `printpath` on `tcp->u_arg[0]`, and returns `RVAL_DECODED`.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h` and generic path-printing support.

Risks: Minimal; behavior is tied to `printpath` handling of unreadable or null tracee strings.

Test signals: Tests should include normal paths, null pointers, and paths requiring truncation or escaping.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/chdir.c -->
