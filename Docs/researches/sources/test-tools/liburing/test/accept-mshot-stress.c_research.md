<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-mshot-stress.c -->
## sources/test-tools/liburing/test/accept-mshot-stress.c

Purpose: stress-tests multishot accept under sustained connections, bursty connection waves, and repeated reconnects.

Important APIs/types/functions: constants set connection counts, burst rounds, reconnect loops, user data, and payload byte. Context structs track listen address, rings, counters, and client state. Helpers include `create_listen_sock`, `arm_mshot_accept`, `stress_client_fn`, `test_accept_mshot_stress`, `burst_client_fn`, `test_accept_mshot_burst`, `reconnect_client_fn`, and `test_accept_mshot_reconnect`.

Control flow: each test arms a multishot accept SQE, starts one or more client threads, then drains CQEs. The stress variant accepts many concurrent clients and verifies one-byte data exchange. The burst variant checks multiple rounds of clustered clients. The reconnect variant repeatedly connects/disconnects to ensure the multishot accept remains armed or is rearmed correctly.

State and persistence behavior: `no_mshot_accept` records unsupported-kernel skip state. Sockets, threads, counters, and the ring are per scenario.

Dependencies and integration points: uses pthreads, TCP sockets, `io_uring_prep_multishot_accept`, CQE `IORING_CQE_F_MORE`, send/recv helpers, and liburing queue APIs.

Risks: high connection counts can hit local resource limits or timing issues. The test must distinguish unsupported multishot accept from real failures. CQE `MORE` handling and rearming behavior are central risk points.

Test signals: strong coverage for multishot accept reliability under load and repeated connection churn.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-mshot-stress.c -->
