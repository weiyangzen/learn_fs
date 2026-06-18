# sources/test-tools/stress-ng/stress-rawsock.c research

Purpose: implements `rawsock`, a Linux raw IPv4 socket stressor that sends self-addressed `IPPROTO_RAW` packets over loopback and verifies payload hashes on receive.

Important APIs, types, and functions: `stress_raw_packet_t` combines an IPv4 header, data counter, and hash. `stress_rawsock_init()` creates a shared stress-ng lock and resets `stop_rawsock`; deinit destroys it. The client waits until all instances mark ready in `g_shared->rawsock.ready`, sends hashed packets, and occasionally exercises `SIOCOUTQ`. The server receives packets, checks hash integrity, uses `SIOCINQ`, and records throughput.

Control flow: `stress_rawsock()` reserves a per-instance port and runs `stress_rawsock_child()` inside `stress_oomable_child`. That child forks a sender and runs the receiver in the parent. The sender applies affinity and scheduler settings, waits for readiness, then sends until stopped. The receiver opens a raw socket, increments shared readiness under lock, receives until stop, validates hashes, records MB/sec, waits for the child, and closes.

State and persistence: shared lock and `g_shared` readiness are runtime-only. Sockets and reserved ports are released on exit; no files persist.

Dependencies and integration: requires Linux `SOCK_RAW`, `IPPROTO_RAW`, `struct iphdr`, `CAP_NET_RAW`, stress-ng locks, OOM wrapper, port reservation, signal handlers, affinity, and hashing. Classified as network and OS.

Risks: global stop and shared readiness are cross-instance coordination points; incorrect lock handling would deadlock startup. Raw sockets may fail under containers. Hash validation catches payload corruption but not all IP header issues. ENOBUFS throttles the client rather than failing.

Test signals: capability skip, lock creation skip, reserved port logs, hash mismatch failures, MB/sec metric, and correct release of port/lock.
