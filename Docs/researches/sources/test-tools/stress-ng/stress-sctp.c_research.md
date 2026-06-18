# sources/test-tools/stress-ng/stress-sctp.c

Purpose: implements `sctp`, a network stressor that forks a client/server pair using SCTP sockets, sends variable-sized messages, verifies payload identity, and exercises many SCTP socket options.

Important APIs/types/functions: `stress_sctp_info` exposes `sctp-domain`, `sctp-if`, `sctp-max-size`, `sctp-port`, and `sctp-sched`. `stress_sctp_sockopts()` round-trips numerous `IPPROTO_SCTP` options through `getsockopt()`/`setsockopt()`, including RTO, association, init, NODELAY, peer params, events, max segment/burst, scheduler, auth/ECN/asconf, and UDP encapsulation where available. `stress_sctp_client()` connects and validates received PID payloads. `stress_sctp_server()` binds/listens/accepts and sends increasing message sizes.

Control flow: `stress_sctp()` resolves domain/interface/port/size/scheduler, verifies optional interface availability, installs SIGPIPE handling, reserves a per-instance port, synchronizes, and forks. The child client retries connect up to 100 times, subscribes to events, optionally sets scheduler, receives messages, and checks the embedded parent PID. The parent server binds, listens, sets reuse and optional nodelay/scheduler, accepts clients, sends messages from a minimum size to configured max size in 16-byte steps, exercises sockopts, and waits for client exit.

State and persistence: state is sockets, reserved port bookkeeping, SIGPIPE count, and optional AF_UNIX socket path cleanup. No durable files are intended.

Dependencies and integration points: requires `libsctp` and `netinet/sctp.h`; networking helpers build sockaddr values, reserve/release ports, wrap port ranges, and validate interfaces. It also uses affinity, signal, kill/wait, and scheduler helpers.

Risks and test signals: SCTP may be unavailable in kernels/containers, ports may be busy, and scheduler sockopts vary by kernel. Signals are skip on unsupported protocol or port reservation failure, bogo increments per successful send, client payload verification, sockopt coverage without fatal unexpected errors, and release of reserved ports.
