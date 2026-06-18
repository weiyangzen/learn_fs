# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/injection.py

Scapy helper for shell ATF packet-injection tests.

Key elements:
- Creates a tun interface, records its name in `tun.txt`, configures RFC 5737 test addresses, starts `/sbin/ping -v -c1 -t1`, receives the echo request, and injects a crafted response.
- Modes:
  - `opts`: echo reply containing 40 NOP IP options.
  - `pip`: ICMP host-unreachable packet quoting an inner packet with options.
  - `reply`: normal echo reply.
- Exits with the child ping process return code.

Dependencies:
- Requires root privileges, `python3`, Scapy, `ifconfig`, tun/tap support, and `/sbin/ping`.

Research notes:
- Cleanup is external in `ping_test.sh`; this script only writes `tun.txt` so the ATF cleanup hook can destroy the created tun interface.
