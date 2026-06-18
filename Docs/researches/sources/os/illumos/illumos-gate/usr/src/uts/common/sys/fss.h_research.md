# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fss.h

## Role

Defines kernel-only structures and helpers for the illumos Fair Share Scheduler class, including CPU partition, project, thread, and zone scheduling state.

## Key Types

- `fsspri_t` and `fssusage_t` are 64-bit priority/usage accounting types.
- `fssbuf_t` stores a sized pointer list allocated for project/zone/pset transitions.
- `fsspset_t` is per-CPU-partition FSS state: locks, cpupart pointer, maximum FSS priority, active shares, project count/list, zone list, and generation.
- `fssproj_t` is per-project-per-partition state: project pointer, pset pointer, thread/runnable counts, shares, tick counters, share percentage, decayed usage, normalized usage, list links, and zone link.
- `fssproc_t` is per-thread FSS state: thread backpointer, project state, flags, quantum time left, ticks, user priorities/limits, schedctl priority, nice value, internal FSS priority, runnable marker, list links, and CPU caps state.
- `fsszone_t` is per-zone-per-partition state with zone pointer, links, share sums, project count, real shares, and runnable project count.

## Functions and Macros

Declares buffer allocation/free and project/pset change helpers. Defines buffer request constants, allocation target constants, `FSS_MAXSHARES`, conversion macros from threads/FSS proc/project to related structures, and flags `FSSBACKQ` and `FSSRESTORE`.

## Risk Notes

This header is not filesystem-related despite the `fss` name; it belongs to scheduler internals. Lock comments indicate per-pset and dispatch-lock protection requirements. Changes affect scheduling-class accounting and zone/project share enforcement.
