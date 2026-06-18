# sources/test-tools/liburing/test/napi-test.c

Purpose: NAPI busy-poll receive test run either directly through `napi-test.sh` or as sender/receiver roles inside network namespaces.

Important APIs/types/functions: `io_uring_register_napi`, `struct io_uring_napi`, `io_uring_prep_recv`, TCP sockets, `setsockopt`, `inet_pton`, `accept`, `connect`, `geteuid`, and role arguments `receive`/`send`.

Control flow: with no args, it locates and runs the shell script. Receiver mode creates a ring with supplied queue flags, registers NAPI preferences, listens on port 9999, accepts a connection, receives 4 KiB buffers through io_uring, and validates byte sequence. Sender mode probes ring creation with the same flags, connects to `10.10.10.20`, and writes 8 MiB of patterned data.

State and persistence behavior: no files. State is TCP stream order, NAPI registration settings, and a shared `current_byte` sequence per process.

Dependencies and integration points: requires root, the companion shell script, network namespaces/veth setup, and NAPI-capable kernel support. It is intended to be invoked as `napi-test.t receive|send <flags>`.

Risks and test signals: skips when not root or ring flags unsupported. Failures include bind/connect errors, receive CQE errors, short/failed writes, or data pattern mismatch.
