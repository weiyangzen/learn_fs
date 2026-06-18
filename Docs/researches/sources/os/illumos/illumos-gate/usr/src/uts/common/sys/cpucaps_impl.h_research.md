# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpucaps_impl.h

## Role

Defines private implementation state for CPU caps.

## Key Constants

- `NOCAP`: alias for `MAXCAP`; disables caps.
- `MAX_USAGE`: maximum usage value, based on `LONG_MAX` for LP64 or explicit 64-bit max for non-LP64.

## Main Structure

- `cpucap_t` stores per-project or per-zone cap state:
  - list linkage.
  - associated project or zone.
  - wait queue for capped threads.
  - kstat pointer.
  - generation for zone caps.
  - scaled cap value and current usage.
  - usage lock.
  - statistics: max usage, below-cap ticks, above-cap ticks.

## Macros

- `CAP_ENABLED()`, `CAP_DISABLED()`
- `PROJECT_IS_CAPPED()`
- `ZONE_IS_CAPPED()`

## Dependencies

Includes kstats, list handling, time, wait queues, and the public `cpucaps.h`.

## Research Relevance

Shows how caps are represented internally and enforced through wait queues, useful when tracing scheduling throttling or resource-control side effects.
