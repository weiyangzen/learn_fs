<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-non-empty.c -->
## sources/test-tools/liburing/test/accept-non-empty.c

Purpose: verifies `IORING_CQE_F_SOCK_NONEMPTY` on accept completions when more pending connections remain.

Important APIs/types/functions: `struct data` holds connector thread/barriers and connection count. `start_accept_listen` creates the listener. `connect_fn` opens a chosen number of client sockets. `setup_thread` initializes barriers and starts the client. `test_maccept` performs accepts in normal or fixed-file mode. `test` runs single-connection and multi-connection cases for a flag/fixed combination.

Control flow: the test initializes a ring, checks for `IORING_FEAT_RECVSEND_BUNDLE` as a feature gate, optionally registers fixed files, starts clients, waits until connections are queued, then issues one accept at a time. It asserts the nonempty flag is clear for single/last accept and set for earlier accepts in a multi-connection backlog.

State and persistence behavior: `no_more_accept` records global skip state when the feature is unavailable. Fixed file slots and accepted sockets live only for one scenario.

Dependencies and integration points: uses TCP sockets, pthread barriers, `io_uring_prep_accept`, `io_uring_prep_accept_direct`, ring-fd/file registration, and CQE flag inspection.

Risks: uses a fixed localhost port (`0x1235 + port_off`), so collisions are possible. Backlog timing matters: connections must be queued before accept checks. Fixed mode requires kernel fixed-file support.

Test signals: validates socket-nonempty CQE flag behavior for normal, defer-taskrun/single-issuer, and fixed-file modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-non-empty.c -->
