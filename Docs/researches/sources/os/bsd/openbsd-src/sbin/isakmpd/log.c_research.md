# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/log.c

Logging and IKE packet capture implementation.

It supports stderr/file/syslog logging, per-class debug levels, verbose logging, debug-level reconfiguration from config, temporary debug toggling, fatal logging through `monitor_exit()`, and fixed-size log buffers suitable for out-of-memory paths. File logging includes timestamps, class names, levels, and a `[priv]` suffix when running as root, with fallback to syslog if writing fails.

The packet capture path writes loopback-style pcap files through monitor-opened files, appending to existing safe regular files or creating restricted new ones. It synthesizes IPv4/IPv6 + UDP headers around ISAKMP payloads, clears the ISAKMP encryption flag in the captured copy for analysis visibility, adds the NAT-T non-ESP marker for port 4500 traffic, computes IP/UDP checksums, and flushes each record.

Notable constraints: capture size is limited by `SNAPLEN`; capture file access goes through the privilege-separation monitor; existing capture files must be regular and not group/world accessible.
