# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/fpopen.c

## Purpose
`fpopen.c` implements a shell-free popen-like helper that splits a command string into argv and executes it directly with `execvp()`.

## Important APIs, Types, and Functions
The exported function is `fpopen(const char *cmd, const char *mode)`. It supports read mode, write mode, and read mode with stderr merged when mode's second character is `&`.

## Control Flow
The function validates mode, tokenizes `cmd` on spaces into up to `MAX_ARGV` entries, creates a pipe, forks, wires stdin or stdout/stderr in the child, executes `prog`, and returns an `fdopen()` stream for the parent side.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the child process and pipe file descriptors. Dependencies are `fork`, `pipe`, `dup2`, `execvp`, stdio, and simple libc parsing. Risks include no quote/escape handling, leaked `buf`, missing fd closes in parent/child, no wait/pclose equivalent, and no `MAX_ARGV` overflow guard. Test signals are executing simple argv-only commands without shell expansion and reading/writing expected data.
