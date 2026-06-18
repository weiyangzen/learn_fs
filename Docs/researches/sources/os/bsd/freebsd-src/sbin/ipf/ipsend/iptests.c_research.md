# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptests.c

This file implements the predefined `iptest` packet-generation suites.

`ip_test1()` exercises IPv4 header edge cases: header length versus packet length, IP version values, packet length mismatches, zero-length fragments, large fragment reassembly scenarios, lost fragments, high fragment offsets, reserved offset bits, and TTL edge values.

`ip_test2()` exercises malformed IP options, including option length greater than packet length and zero-length RR/TS/security/source-route/SATID options.

`ip_test3()` generates ICMP type/code sweeps and shortened ICMP packets.

`ip_test4()` tests UDP length mismatches, source/destination port edge values, and small MTU handling.

`ip_test5()` tests TCP flag combinations, sequence/ack/window edge values, urgent pointer behavior, TCP data offset values, source/destination port edge values, and a LAND-style self-connect case. Some subtests inspect live kernel TCP PCB state through `find_tcp()`.

`ip_test6()` creates repeated overlapping/fragmented UDP packets to pressure mbuf/reassembly behavior.

`ip_test7()` sends randomized IPv4 packets in two batches, including constrained fragment flags.

Important dependencies include `ipsend.h`, `send_ip()`, `send_tcp()`, `send_udp()`, `send_icmp()`, backend `initdevice()`, and kernel TCP state helpers.

Implementation notes and risks:
- This code intentionally emits malformed traffic and should only be used in controlled test networks.
- It is highly OS-structure dependent for TCP PCB tests.
- Uses sleep/select/nanosleep pacing through the `PAUSE()` macro.
