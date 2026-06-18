# sources/test-tools/stress-ng/stress-rawudp.c research

Purpose: implements `rawudp`, a Linux raw UDP socket stressor that crafts IPv4/UDP packets with `IP_HDRINCL`, sends them to a selected interface address, and verifies the embedded sender PID on receive.

Important APIs, types, and functions: `stress_rawudp_supported()` requires `CAP_NET_RAW`. `stress_rawudp_client()` creates a raw UDP socket per send iteration, sets `IP_HDRINCL`, fills IP and UDP headers plus PID payload, computes the IPv4 checksum, sends, and closes. `stress_rawudp_server()` binds a raw UDP socket, filters received packets by source address, protocol, and source port, verifies PID payload, and emits byte and packet rate metrics.

Control flow: `stress_rawudp()` optionally resolves `rawudp-if`, otherwise uses loopback, reserves a per-instance port, installs signal handling, synchronizes, forks a client pinned near the parent CPU, and runs the server in the parent until stopped. Parent kills/reaps the client and releases the port.

State and persistence: transient sockets and port reservations only; no persistent network configuration changes.

Dependencies and integration: Linux UDP/IP headers, raw socket support, inet helpers, stress-ng interface lookup, port reservation, affinity, checksum, signal, and kill helpers. Registers as network and OS with `VERIFY_ALWAYS`.

Risks: raw socket capability and container policies determine availability. The client opens/closes sockets rapidly, intentionally stressing allocation paths. PID payload verification assumes loopback/self-addressed traffic and may fail if unrelated raw UDP traffic matches filters.

Test signals: capability and port-reservation skips, interface fallback message, bind/socket failures, data-check failure logs, MB/sec and packets/sec metrics, and clean child reap.
