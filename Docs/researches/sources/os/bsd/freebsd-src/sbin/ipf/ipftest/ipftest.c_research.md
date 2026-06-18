# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ipftest.c

`ipftest.c` is the main offline packet-filter test runner. It loads IPFilter/NAT/pool rules into a user-space IPFilter instance, reads packets from text/hex/pcap inputs, runs them through `ipf_check()`, and prints the resulting action and packet details.

Major behaviors:
- Initializes parser state, loads all IPFilter modules, creates and initializes all softc state, and enables filtering through the local ioctl path.
- Accepts input formats through `-F pcap|hex|text`; defaults to text.
- Loads filter rules with `-r`, NAT rules with `-N`, pools with `-P`, and tuning with `-T`.
- Supports IPv6 selection, checksum fixing, debug/verbose/hex/brief modes, output interface saving, source-direction override, binary log draining, and final dump output.
- For each packet, determines interface and direction, optionally fixes checksums, calls `ipf_check()`, prints pass/block/auth/account/nomatch/bad-packet style results, then flushes transient state and writes outbound packets when requested.
- Cleans up softc, modules, mutexes/rwlocks, and optionally aborts under `FINDLEAKS`.

Local ioctl adapters:
- `ipftestioctl`, `ipnattestioctl`, `ipstatetestioctl`, `ipauthtestioctl`, `ipscantestioctl`, `ipsynctestioctl`, and `ipooltestioctl` forward ioctl calls to the in-process softc using the correct IPL log unit.
- `kmemcpy()` and `kstrncpy()` are direct user-space memory copies for code paths expecting kernel-memory access.

Diagnostics:
- `dumpnat()` prints configured NAT rules, active sessions, proxy activity, and hostmaps.
- `dumpgroups()` and `dumprules()` print configured groups and rule lists.
- `drain_log()` drains all IPFilter logs into a file.
- `fixv4sums()` recomputes IPv4 and L4 checksums for TCP/UDP/ICMP.
