# sources/user-network-fs/samba/source3/librpc/idl/perfcount.idl

## Purpose
`perfcount.idl` defines Windows performance counter data structures used by Samba's perfcount code. It mirrors PERF object, counter, instance, block, and top-level data-block layouts.

## Important APIs, types, and functions
- Constants encode PERF size, type, number/counter/text format, timer base, delta/inverse/multi behavior, display suffix, and detail level flags.
- `SYSTEMTIME` models the timestamp structure.
- `PERF_COUNTER_DEFINITION`, `PERF_COUNTER_BLOCK`, `PERF_INSTANCE_DEFINITION`, `PERF_OBJECT_TYPE`, and `PERF_DATA_BLOCK` define nested performance data.

## Control flow
There is no executable code. The intended flow is that perfcount producers populate a `PERF_DATA_BLOCK` with object definitions, counter definitions, optional instances, and counter data blocks, then generated NDR marshals or unmarshals it.

## State and persistence behavior
The structures represent a snapshot of performance data rather than persistent state. Length fields such as `ByteLength`, `TotalByteLength`, `HeaderLength`, `NameOffset`, and `NameLength` govern parsing of variable-length data.

## Dependencies and integration points
The IDL is standalone aside from `idl_types.h` and is built into `NDR_PERFCOUNT`. It integrates with registry/performance counter responders and any code that emits Windows-compatible performance data.

## Risks and edge cases
Variable-length buffers and offset/length math are the main risks. The comment notes 64-bit alignment before `PerfTime` fields; incorrect alignment or byte-length values can break Windows clients. `NumInstances` can be `PERF_NO_INSTANCES` in Windows semantics, so parser behavior around negative constants and arrays needs care.

## Test signals
Test NDR round trips for single-instance, multi-instance, and no-instance objects; validate byte offsets and 64-bit alignment; fuzz length fields; and compare emitted data against Windows perf counter clients.
