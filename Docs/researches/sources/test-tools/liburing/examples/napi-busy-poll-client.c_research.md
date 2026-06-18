# sources/test-tools/liburing/examples/napi-busy-poll-client.c

## sources/test-tools/liburing/examples/napi-busy-poll-client.c

Purpose: UDP ping client demonstrating io_uring NAPI busy-poll registration, optional SQPOLL/DEFER_TASKRUN/COOP_TASKRUN modes, and RTT measurement.

Important APIs/types/functions: `struct ctx`, `struct options`, `io_uring_napi`; `sendPing`, `receivePing`, `completion`, `recordRTT`, `printStats`, `reportNapi`; `io_uring_register_napi`, `io_uring_unregister_napi`, `io_uring_submit_and_wait_timeout`.

Control flow: parse address/port/ping count/busy options, connect UDP socket, configure ring flags, optionally register NAPI busy poll preferences, optionally use zero timeout pointer for busy looping, raise scheduler to SCHED_FIFO if permitted, send initial timestamp ping, then alternate send and receive completions until count is exhausted. First receive reports incoming NAPI id; later receives record RTT and queue next send.

State and persistence: uses socket connection state, in-memory RTT array, and ring registration state. No files.

Dependencies/integration: Linux NAPI socket options and liburing NAPI APIs, UDP peer server, optional realtime scheduler privilege.

Risks: uses `strcpy` into fixed-size option buffers without bounds checks. `-s` and `-d` parsing use `!!atoi(optarg)` even options are declared without obvious argument in usage. `optarg` is referenced in some error paths after `inet_pton`. RTT uses realtime clock, not monotonic.

Test signals: NAPI id print, RTT min/avg/max/mdev output, unregister verification of returned NAPI settings.
