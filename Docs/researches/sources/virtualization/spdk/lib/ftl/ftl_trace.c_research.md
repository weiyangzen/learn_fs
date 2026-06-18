# File Research: sources/virtualization/spdk/lib/ftl/ftl_trace.c

Debug-only SPDK trace integration for FTL.

When `DEBUG` is defined, the file registers FTL trace owner/type and tracepoint descriptions for internal/user sources, including band relocation/write, limits, read/write/trim scheduling/submission/completion, and metadata read/write events.

Runtime helpers:
- `ftl_trace_alloc_id` atomically allocates event IDs.
- `ftl_trace_reloc_band` and `ftl_trace_write_band` emit internal band events.
- `ftl_trace_lba_io_init` records user IO scheduling.
- `ftl_trace_submission` records read/write/trim submission addresses and counts.
- `ftl_trace_completion` records read/write/trim completion location/type.
- `ftl_trace_limits` records throttling/limit state.

In non-debug builds these functions are macro-elided by `ftl_trace.h`, so there is no runtime tracing cost.
