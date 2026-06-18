# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_shell.c

## Purpose
Implements FreeBSD's `#!` shell-script image activator for `execve(2)`. It recognizes scripts, parses the interpreter line, rewrites the exec argument vector, and registers the handler through the kernel exec switch.

## Key Elements
- Defines endian-aware `SHELLMAGIC` for `#!`.
- Enforces `MAXSHELLCMDLEN <= PAGE_SIZE` because the exec path maps only the first page.
- Enforces `MAXSHELLCMDLEN >= MAXINTERP + 3`.
- Main entry point: `exec_shell_imgact(struct image_params *imgp)`.
- Registration: `EXEC_SET(shell, shell_execsw)` with `.ex_name = "#!"`.

## Behavior
`exec_shell_imgact()`:
- Rejects non-`#!` files by returning `-1`, allowing other image activators to try.
- Rejects recursive shell interpretation using `IMGACT_SHELL`.
- Uses `VOP_GETATTR()` to limit parsing to actual file size rather than blindly trusting the mapped page.
- Parses interpreter path after leading spaces/tabs.
- Rejects empty interpreter paths with `ENOEXEC`.
- Rejects interpreter paths at or above `MAXINTERP` with `ENAMETOOLONG`.
- Parses the remainder of the first line as a single optional argument string, trimming trailing spaces/tabs.
- Requires a newline or NUL before `MAXSHELLCMDLEN`; otherwise returns `ENOEXEC`.
- Uses `imgp->args->fname` as script name, or synthesizes `/dev/fd/<fd>` through `sbuf` for fd-backed exec.
- Calls `exec_args_adjust_args()` to remove the original `argv[0]` and insert interpreter, optional argument string, and script filename.
- Sets `imgp->interpreter_name` to the rewritten argument buffer so the generic exec path can execute the interpreter.

## Research Notes
The historical comment is significant: FreeBSD intentionally passes all post-interpreter text as one argument instead of tokenizing it in-kernel. This keeps quoting/comment interpretation in the interpreter, not in the kernel.

## Interfaces And Dependencies
Depends on exec argument management from `kern_execve.c`-side helpers, vnode metadata via `VOP_GETATTR()`, and `sbuf` for `/dev/fd` fallback construction.
