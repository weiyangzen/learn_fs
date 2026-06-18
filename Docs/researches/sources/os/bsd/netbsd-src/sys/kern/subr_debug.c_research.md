# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_debug.c

## Summary
Provides optional DEBUG-kernel allocation/free validation by tracking pointer membership in caller-supplied lists.

## Main Responsibilities
- Initializes the global freecheck lock and optional fixed pool of tracking items.
- `freecheck_out()` records that an address is checked out and panics if already present.
- `freecheck_in()` removes a checked-out address and panics or enters DDB if absent.

## Important Behavior
Tracking is enabled by setting `debug_freecheck`. The fixed pool is allocated from wired kernel memory during `debug_init()`. If the pool runs out, the code prints a one-time warning and disables effective tracking by changing `debug_freecheck`.

## Dependencies
Uses `uvm_km_alloc()`, CPU simple locks, `splvm()`, atomic swap, optional DDB, and DEBUG kernel configuration.

## Risks
The feature is deliberately expensive and not enabled by default. Once tracking slots are exhausted, further coverage is degraded.
