# File Research: sources/os/bsd/openbsd-src/sbin/unwind/resolver.h

`resolver.h` declares control-facing resolver state and telemetry structures. `enum uw_resolver_state` orders states as dead, unknown, resolving, and validating, with string names used for status display.

The latency histogram bucket limits range from sub-10ms through 1000ms and an `INT64_MAX` catchall. `struct ctl_resolver_info` carries resolver state, type, median latency, lifetime histogram, and decayed recent histogram. `struct ctl_forwarder_info` reports autoconf forwarder IP, interface index, and source. `struct ctl_mem_info` reports cache usage and maximums for message, rrset, key, and negative caches.

The header exports the resolver process entry point and imsg compose helpers for sending messages to main and frontend processes.
