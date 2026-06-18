<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf_event_struct.h -->
# sources/test-tools/strace/src/perf_event_struct.h

Purpose: local UAPI-compatible definitions for perf event structures used by decoders.

Important APIs/types/functions: `struct perf_event_attr`, `struct perf_event_query_bpf`, `PERF_PMU_TYPE_SHIFT`, and `PERF_HW_EVENT_MASK`.

Control flow: no executable flow; structure layout encodes versioned perf attr fields from ver0 through ver9 and query-bpf flexible array header.

State and persistence behavior: no state.

Dependencies and integration points: included by `perf.c` and `perf_ioctl.c`; layout must match kernel UAPI enough for tracee memory decoding across personalities.

Risks: bitfield order and structure growth are ABI-sensitive. Missing newer fields or wrong reserved widths causes incorrect perf output.

Test signals: compile-time structure size/offset expectations, perf attr version-size tests, and `PERF_EVENT_IOC_QUERY_BPF` id-array decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf_event_struct.h -->
