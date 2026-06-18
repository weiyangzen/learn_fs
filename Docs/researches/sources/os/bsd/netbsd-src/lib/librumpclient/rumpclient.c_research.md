# File Research: sources/os/bsd/netbsd-src/lib/librumpclient/rumpclient.c

Read completely: 1263 lines.

Implements the client side of the rump syscall proxy protocol. It connects to the server described by `RUMP__PARSEDSERVER` or `RUMP_SERVER`, performs handshakes, sends syscall request frames, waits for responses, and services server callbacks for copyin, copyout, anonymous mmap, and signal delivery.

The transport preserves host syscall access through `dlsym(RTLD_NEXT)` or static fallbacks, so rumphijack can intercept ordinary calls while rumpclient still reaches real host `socket`, `connect`, `poll`/`kevent`, `read`, `sendmsg`, and related functions. On BSD it uses kqueue, on Linux signalfd, and otherwise poll/signal masking to avoid signal handling while holding communication locks.

Connection management includes optional reconnect behavior, generation checks for waiters, a special `holyfd` monitored descriptor, descriptor relocation to avoid stdio collisions, and close-notification handling so intercepted close/dup2/fclosem cannot accidentally destroy the rump connection.

Fork/exec support uses prefork authentication, reconnects the child with `HANDSHAKE_FORK`, preserves state for vfork parent handling, and passes existing connection descriptors through `RUMPCLIENT__EXECFD` during exec. `rumpclient_daemon()` builds on this machinery with a manual daemonization sequence.
