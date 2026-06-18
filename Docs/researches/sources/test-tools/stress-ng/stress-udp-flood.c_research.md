## sources/test-tools/stress-ng/stress-udp-flood.c

Purpose: Implements `udp-flood`, a UDP send flood stressor that varies datagram size and alternates between sequential and random reserved destination ports.

Important APIs/types/functions: `stress_udp_flood_info`, `stress_udp_flood`, options `udp-flood-domain`, `udp-flood-if`, and `udp-flood-max-size`; uses `socket`, `sendto`, `ioctl(SIOCOUTQ)`, stress-ng sockaddr construction, interface validation, and port reservation.

Control flow: reads settings, validates optional interface, creates a datagram socket, builds a target sockaddr, then repeatedly reserves one sequential port and one random port. It fills a stack buffer with rotating ASCII bytes, sends to both ports, increases payload size up to the configured maximum, periodically checks socket output queue, and releases/recycles ports every 16384 changes.

State and persistence: maintains transient socket fd, sockaddr, byte/send counters, failure count, and reserved port state. No persistent files are created.

Dependencies/integration: relies on `core-net`, domain masks, global maximize/minimize flags, and stress-ng metrics.

Risks: intentionally resembles flood traffic; can be blocked by interface/domain mismatch, unsupported protocol, packet filtering, or network buffer pressure. A 100 percent `sendto` failure rate is treated as failure.

Test signals: `VERIFY_ALWAYS`; reports MB/sec, sendto/sec, and percent successful sends.
