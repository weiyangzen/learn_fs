# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/test_ping.py

Pytest/Scapy ping regression harness using a single vnet and tun interfaces.

Key elements:
- Provides a Scapy fallback shim so tests can be enumerated even when Scapy is absent.
- `build_response_packet` mutates the captured echo request into echo replies or ICMP error packets, including special cases for no payload, TCP/UDP quoted packets, timestamp warp, wrong payload byte, and not-this-process identifiers.
- `generate_ip_options` constructs EOL/NOP/RR/LSRR/SSRR/unknown IP options and disables kernel IP option processing when necessary.
- `pinger` creates/configures a tun interface, runs `/sbin/ping`, receives outbound echo packets, injects crafted replies/errors, optionally sends duplicates, and returns a `CompletedProcess`.
- `redact` normalizes dynamic output such as addresses, hop limits, TTL, timings, hex dumps, and negative time deltas.
- `TestPing` sets IPv4/IPv6 test prefixes, validates many direct ping command outputs, validates common `ping -4`/`ping -6` argument errors, and parametrically tests crafted ICMP/IP edge cases.

Dependencies:
- `atf_python.sys.net.vnet`, `IfaceFactory`, `SingleVnetTestTemplate`, `ToolsHelper`, pytest markers, Scapy, tun interfaces, root privileges for packet injection.

Research notes:
- The test matrix exercises normal replies, no-reply exits, quiet mode, audible missed packets, source address output, malformed IP options, truncated quoted packets, DF flags, wrong payload reporting, and time-warp clamping.
- Expected outputs are mostly exact strings, with redaction applied only for fields that are intentionally variable.
