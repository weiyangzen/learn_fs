# File Research: sources/virtualization/spdk/lib/ftl/ftl_trace.h

Declares the debug trace API and provides no-op macros outside `DEBUG`.

Defines:
- `FTL_TRACE_INVALID_ID`
- `enum ftl_trace_completion`: invalid/cache/disk completion source
- `struct ftl_trace`: monotonically increasing event ID counter

In debug builds, it declares allocation and event-recording helpers for relocation, writes, LBA IO lifecycle, submissions, completions, and limits. In non-debug builds, all trace calls compile away and allocation returns `FTL_TRACE_INVALID_ID`.

Role: gives FTL code a uniform trace interface without sprinkling `#ifdef DEBUG` through call sites.
