# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/pager.c

## Purpose
`pager.c` provides the ss pager abstraction used for request lists and help text.

## Important APIs, Types, and Functions
Public functions are `ss_safe_getenv()`, `ss_pager_create()`, and `ss_page_stdin()`. Internal helper `write_all()` supports fallback output.

## Control Flow
`ss_pager_create()` either forks a child connected to a pipe and returns the write end, or opens `/dev/tty` in no-fork builds. `ss_page_stdin()` closes extra fds, resets SIGINT handling, obtains `PAGER` securely or defaults to `more`, execs it, and falls back to copying stdin to stdout if exec fails.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_pager_name` and child pipe descriptors. Dependencies include fork/pipe/exec, secure getenv/prctl behavior, signals, and `more`. Risks include limited fd close range, child wait handled by callers, environment suppression in privileged contexts, and fallback output losing pager behavior. Test signals are help/list output paged through `PAGER` and fallback display when no pager exists.
