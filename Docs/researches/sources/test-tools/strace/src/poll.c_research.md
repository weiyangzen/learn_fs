<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poll.c -->
# sources/test-tools/strace/src/poll.c

Purpose: decodes `poll` and `ppoll` time32/time64 variants and produces concise return aux strings for ready fds and remaining timeout.

Important APIs/types/functions: `print_pollfd`, `decode_poll_entering`, `decode_poll_exiting`, `do_poll`, `do_ppoll`, `SYS_FUNC(poll_time32)`, `poll_time64`, `ppoll_time32`, and `ppoll_time64`.

Control flow: on entry, prints the `pollfd` array and nfds; `poll` prints integer timeout, `ppoll` prints timespec pointer and sigmask/size. On exit, successful calls scan the array for nonzero `revents`, build `tcp->auxstr`, and include timeout-left text when applicable.

State and persistence behavior: uses a static 1024-byte aux buffer inside `decode_poll_exiting`; no durable state across calls beyond `tcp->auxstr`.

Dependencies and integration points: syscall table time variants, poll flag xlats, array printers, timespec printers, sigset printers, and `xstring` bounded append helpers.

Risks: aux string truncation must remain syntactically understandable. Size arithmetic can overflow for huge nfds but is guarded by address range checks and fetch failures.

Test signals: ready fd arrays, timeout return, errors, negative fd entries, ppoll sigmask, time32/time64 paths, aux truncation, and modified timeout-left output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poll.c -->
