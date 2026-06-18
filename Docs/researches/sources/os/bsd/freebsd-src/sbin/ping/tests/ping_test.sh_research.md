# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/ping_test.sh

ATF shell smoke and regression tests for `ping` and `ping6`.

Key elements:
- `require_ipv4` and `require_ipv6` skip tests when localhost address families are unavailable.
- Covers basic IPv4/IPv6 one-packet pings, source-address selection with `-S`, invocation through `ping6`, option parsing for `-t4`/`-t6`, mutually exclusive `-4`/`-6`, nonexistent host failures, and `ping6 -4` rejection.
- Packet injection tests run `injection.py` in `opts`, `pip`, and `reply` modes and destroy the tun interface in cleanup hooks.
- `timestamp_origin` enables `net.inet.icmp.tstamprepl`, runs `ping -Mt`, extracts originate/receive timestamps, allows a two-second difference, and restores the sysctl.
- `check_ping_statistics` normalizes timing, address, `ttl`, and `hlim` fields before diffing fixture output.

Dependencies:
- ATF shell framework, `getaddrinfo`, `ping`, `ping6`, `sysctl`, `date`, and optional Scapy for injection cases.

Research notes:
- Tests with mutable network state are either root-only or require `allow_sysctl_side_effects`.
- Injection tests are exclusive at Makefile metadata level because fixed addresses and `tun.txt` would otherwise conflict.
