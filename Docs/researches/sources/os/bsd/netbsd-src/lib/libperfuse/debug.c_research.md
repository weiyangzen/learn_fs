# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/debug.c

Read completely: 276 lines.

This implements perfuse tracing and debug formatting. It maps FUSE opcodes to names, defines queue-type strings, formats selected inbound operation payloads, records trace start/end timestamps, prunes completed traces past `PERFUSE_TRACECOUNT_MAX`, and dumps trace history plus per-op timing statistics.

`perfuse_opname` linear-searches the opcode table and returns `UNKNOWN` for unmatched operations. `perfuse_opdump_in` currently formats `FUSE_LOOKUP` path payloads. `perfuse_trace_begin` records opcode, initial status, timestamp, node path, and extra operation text, then appends to `ps_trace`. `perfuse_trace_end` records completion time/error and prunes old completed traces. `perfuse_trace_dump` truncates and rewinds an output file, prints individual traces, computes min/avg/max latency by opcode, and prints global node/exchange counts.

Security/reliability notes: `perfuse_opdump_in` uses a static buffer, so concurrent calls race. `perfuse_trace_dump` indexes arrays by `pt_opcode`; opcodes outside `FUSE_OPCODE_MAX` would be unsafe if inserted into traces.
