# File Research: sources/local-fs/btrfs-progs/kernel-lib/trace.h

## Purpose
No-op tracepoint stubs for userspace builds that share code with kernel-origin btrfs components.

## Contents
Forward declares several btrfs structures and defines empty inline functions for workqueue, ordered work, extent state, extent bit, and COW block tracepoints.

## Integration
Lets shared code compile without carrying Linux kernel tracing infrastructure.

## Risks
- All trace calls are compiled away; diagnostics relying on kernel tracepoints are unavailable in btrfs-progs.
- Function signatures must stay synchronized with shared code call sites.
