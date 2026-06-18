# File Research: sources/os/bsd/netbsd-src/sys/sys/rngtest.h

Read completely: 49 lines.

This header defines a small FIPS 140 random-number generator test state. It sets the test window to 20,000 bits, defines `rngtest_t` with sample bytes, poker/run counters, error count, and source name, and declares `rngtest`.

Risks: no implementation here. Consumers must treat the result as a statistical health check, not proof of cryptographic quality.
