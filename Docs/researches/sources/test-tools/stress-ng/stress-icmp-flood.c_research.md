# sources/test-tools/stress-ng/stress-icmp-flood.c

## Purpose
`stress-icmp-flood.c` sends raw IPv4 ICMP echo packets to localhost to stress raw socket send paths, checksum generation, and loopback/network stack processing.

## Important APIs, Types, And Functions
Option `icmp-flood-max-size` enables randomized payloads up to the IPv4 packet limit; otherwise payloads are capped at 1000 bytes. `stress_icmp_flood_supported()` requires `CAP_NET_RAW`. `stress_icmp_flood()` opens `socket(AF_INET, SOCK_RAW, IPPROTO_RAW)`, enables `IP_HDRINCL` and `SO_BROADCAST`, prepares `struct iphdr` and `struct icmphdr`, fills random payload bytes, sends packets with `sendto()`, and records send and throughput metrics.

## Control Flow
After capability and feature checks, the stressor chooses payload limit, opens/configures the raw socket, sets destination/source to `127.0.0.1`, waits at the sync barrier, initializes IP/ICMP headers, then loops: choose payload length, update total length/id/sequence, perturb payload, compute ICMP checksum, send the packet, count failures or bytes, increment bogo ops, and advance sequence. Exit computes successful send rate, MB/sec, and percent success.

## State And Persistence
State is in the raw socket, stack packet buffer, counters, and local metrics. It writes no files but injects packets into the local network stack.

## Dependencies And Integration Points
It depends on Linux/Unix IP and ICMP headers, stress-ng capability checks, checksum helper `stress_net_ipv4_checksum()`, random data helpers, metrics, and verify flags.

## Risks
Requires root or `CAP_NET_RAW`; otherwise it must skip. Large randomized packets may fragment or fail. The packet buffer is stack-allocated near the maximum IP length. The code counts send failures but does not inspect receive behavior, so network-stack acceptance is inferred from `sendto()`.

## Test Signals
Signals include correct skip without capability, successful raw socket configuration, nonzero sendto calls/sec, reasonable success percentage, checksum correctness, and no stack/buffer overruns with max-size enabled.
