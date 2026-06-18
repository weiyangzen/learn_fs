# sources/test-tools/stress-ng/stress-epoll.c

Purpose: implements `epoll`, a network/OS stressor that drives many short socket connections through epoll server processes, exercising `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, and optionally `epoll_pwait2`.

Important APIs/types/functions: `stress_epoll_pwait()` selects `epoll_pwait2` when available and falls back to `epoll_pwait`. `epoll_spawn()` starts synchronized server children. `epoll_set_fd_nonblock()`, `epoll_ctl_add/mod/del()`, `epoll_notification()`, `epoll_recv_data()`, `test_eloop()`, and `test_epoll_exclusive()` cover normal and invalid epoll operations. `epoll_client()`, `epoll_server()`, and `stress_epoll()` coordinate traffic.

Control flow: `stress_epoll()` parses domain/port/socket limits, reserves ports, forks one AF_UNIX server or up to four INET servers, sync-starts them, and runs a client loop. The client cycles ports, creates sockets, arms a realtime timer to bound blocking connects, sends a random buffer, and closes. Each server binds/listens, creates epoll fds, registers the listen socket, accepts nonblocking clients, adds fds to epoll, reads ready data, handles HUP/ERR, and probes invalid arguments, bad fds, circular epoll membership, unmapped event buffers, and exclusive-event restrictions.

State and persistence behavior: server state is fd tables, port reservations, optional AF_UNIX socket paths, epoll event arrays, and timer state. It persists no durable data. Cleanup kills servers, releases ports, unlinks AF_UNIX paths, closes fds, and unmaps synchronized PID storage.

Dependencies and integration points: requires epoll headers/functions, librt timer APIs, and glibc 2.3.2 support. It integrates with stress-ng network address/port helpers, synchronized child start, process-state, fork retry, scheduler, signal, bad-fd, and mapped guard-page helpers.

Risks: connection-table saturation, `TIME_WAIT`, fd exhaustion, unavailable ports, and domain-specific socket cleanup can affect behavior. The intentional EFAULT/EINVAL/ELOOP probes are kernel-version-sensitive; SIGSEGV recovery guards invalid event-buffer tests. AF_INET/AF_INET6 runs can be noisier than AF_UNIX because they consume real local port ranges.

Test signals: run default AF_UNIX and explicit AF_INET/AF_INET6 with small and large `--epoll-sockets`, confirm server children exit, ports are released, no AF_UNIX socket paths remain, and verification failures only appear for unexpected successful invalid epoll calls.
