# File Research: sources/os/plan9/9front/sys/src/9/port/devproc.c

Purpose: Implements `#p`, the Plan 9 process filesystem for inspecting and controlling processes.

Key logic:
- Root lists `trace` plus one directory per live process; process qids encode file type, process table slot, and pid/version for stale-channel detection.
- Per-process files expose args, ctl, fd, namespace, memory, notes, note groups, registers, fp registers, status, text, wait records, profile data, syscall traces, and watchpoints.
- `procopen` enforces permissions, handles special `/proc/trace`, protects kernel processes/private memory, and redirects `text` opens to the text image channel.
- `procread` implements status formatting, namespace and fd reconstruction, wait queue consumption, note consumption, user memory reads through `segio`, and privileged kernel memory reads.
- `procwrite` updates args, writes stopped-process memory/registers/fpregs, posts notes, changes note ids, writes watchpoints, and dispatches ctl commands.
- `procctlreq` handles process control: kill, stop/start/startstop/startsyscall, waitstop, priority, wired CPU, private memory, profiling, interrupt flags, fd closing, tracing, and EDF real-time parameters.
- Watchpoint support parses textual `rwx addr len` rows and delegates validation/programming to architecture-specific `setupwatchpts`.

Dependencies and integration:
- Integrates with process tables, segment/page VM, note delivery, fd and namespace groups, scheduler priority/EDF code, tracing, `Segio`, architecture register helpers, and pool secrecy checks.

Risks and notes:
- Permission rules are intentionally uneven: debugging-readable files such as `fd`, `ns`, and `status` remain broadly readable.
- Memory writes require the target to be stopped and can convert text to data via `txt2data`.
- `/proc/trace` is eve-only and single-open; it uses a ring of `Traceevent` records.
