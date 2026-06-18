# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptest.c

This is the `iptest` command-line driver for running predefined packet filter stress tests.

It parses destination, optional source, gateway, device, MTU, selected test number `1` through `7`, and point-test selector. It resolves addresses, prints the chosen packet parameters, then dispatches to `ip_test1()` through `ip_test7()` or runs all tests by default.

Important dependencies include `ipsend.h` and the test implementations in `iptests.c`.

The tool constructs a large packet buffer and passes it to test routines, which mutate packet fields to generate malformed, edge-case, and stress packets.
