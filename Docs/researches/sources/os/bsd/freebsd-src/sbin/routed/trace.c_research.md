# File Research: sources/os/bsd/freebsd-src/sbin/routed/trace.c

## Summary
Tracing and formatting support for `routed`. It manages trace files/levels, logs daemon actions, dumps route/interface state, formats route names and flag bitfields, and traces RIP packets including authentication and route contents.

## Main Responsibilities
- Opens, reopens, closes, and flushes trace output.
- Raises/lowers trace level from command-line, RIP trace commands, or SIGUSR1/SIGUSR2.
- Restricts remote trace-file names to configured/approved paths.
- Formats IPv4 addresses, route names, interface flags, route state flags, metrics, tags, timers, and spare route slots.
- Dumps current interface and route table state.
- Traces RIP request/response packets and RIP trace-on/trace-off commands.
- Displays RIP password or MD5 authentication metadata in packet traces.

## Key Elements
- `tracelevel`, `new_tracelevel`, `ftrace`: global trace control state.
- `set_tracefile()` and `tracelevel_msg()`: controlled trace-file and level transitions.
- `addrname()`, `rtname()`, `trace_bits()`: reusable formatting helpers.
- `trace_if()`, `trace_change()`, `trace_add_del()`, `trace_upslot()`: route/interface action logging.
- `trace_dump()` and `walk_trace()`: full daemon-state dump.
- `trace_rip()`: RIP packet summary/content decoder.

## Dependencies And Integration
Uses `defs.h`, `pathnames.h`, RIP command names, route/interface structures, radix-tree walking, and daemon time globals. Trace output is consumed by other `routed` modules through `trace_act`, `trace_misc`, `trace_pkt`, and route formatting helpers.

## Research Notes
Trace control is deliberately conservative for network-requested trace files: arbitrary names are rejected unless they match the initial trace path or configured trace directory policy.
