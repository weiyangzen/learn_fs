# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc.h

## Purpose
Provides the public kernel entry point for the system duty-cycle scheduling class support.

## Main Interfaces
- `SYSDC_THREAD_BATCH`: marks a thread as doing batch processing.
- `sysdc_thread_enter(struct _kthread *, uint_t, uint_t)`: moves/configures a thread for SDC behavior.

## Dependencies And Relationships
Includes `sys/types.h` and forward-declares `struct _kthread`. The implementation details live in `sysdc_impl.h`.

## Research Notes
This is the narrow public boundary; most SDC state and accounting is deliberately hidden in the implementation header.
