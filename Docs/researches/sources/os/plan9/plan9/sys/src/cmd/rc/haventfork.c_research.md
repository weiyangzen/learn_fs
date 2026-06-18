# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/haventfork.c

Fallback rc process-control implementation for environments without fork.

Strategy:
- `havefork = 0`.
- `rcargv()` builds an argv that re-invokes rc with `-S`/`-Se -c <script>` plus current `$*`.
- `Xasync()`, `Xbackq()`, `Xpipe()`, and `Xsubshell()` run script snippets via `ForkExecute()` instead of in-process forked interpreter frames.
- `Xpipefd()` is unsupported and aborts.
- `execforkexec()` searches `$path` and starts commands with mapped fds via `ForkExecute()`.

Risk/notes:
- No-fork mode depends on `code.c` emitting command strings for affected constructs.
- Backquote splitting here is byte-based, unlike the rune-aware fork implementation.
- Pipefd is not portable in this mode.
