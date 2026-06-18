# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tuneable.h

## Purpose
Kernel tunable structure definition for historical VM/system parameters.

## Main Interfaces
- Defines `struct tune` with tunable fields including maximum process size, core size, stack size, and other system sizing values.
- Defines `GETPGSMSK` as `PG_REF | PG_NDREF`.

## Dependencies And Relationships
Used by old kernel code and compatibility paths expecting a `tune` structure. It relates to VM/page flag handling through `GETPGSMSK`.

## Research Notes
This is largely historical; modern illumos tunables are typically handled through more specific subsystem variables.
