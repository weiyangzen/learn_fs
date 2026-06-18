# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipmon.h

## Purpose
Defines shared structures and flags for IPFilter log monitoring configuration/actions.

## Main Elements
- `ipmon_msg_t` describes a log message plus payload, timestamp, and log level.
- `ipmon_saver_t` defines pluggable storage/output callbacks.
- `ipmon_saver_int_t` and `ipmon_doing_t` link configured saver instances.
- `ipmon_action_t` represents match criteria and actions for log events.
- Defines match flags such as direction, src/dst IP, ports, group, interface, result, type, and log tag.
- Defines runtime flags for syslog, resolving, hex output, tail mode, verbosity, NAT/state/filter logging, and port-number display.
- Declares configuration and action helper functions.

## Dependencies And Integration
Used by `ipmon` parser and runtime code to match log events and route them to configured outputs.

## Risk Notes
The structure mixes matching state, rate counters, and action lists; changes must stay aligned with `ipmon` parser/runtime expectations.
