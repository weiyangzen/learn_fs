# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/loadavg.h

## Role

Load-average constants, kernel accumulator layout, and kernel/user `getloadavg()` declarations.

## Structure

Defines indexes for 1, 5, and 15 minute load averages, number of stats, sample-table sizes, and `struct loadavg_s` containing current index, recorded length, temporary total, and an `hrtime_t` ring/table of load samples.

## Dependencies And Consumers

The file assumes `hrtime_t` is already available to consumers. Kernel builds declare `getloadavg(int *, int)`; user builds declare `getloadavg(double [], int)`.

## Important Details

The kernel and user prototypes intentionally differ in result type. Code including this header must be compiled with the correct `_KERNEL` context.

## Research Notes

Read completely: 68 lines, 1686 bytes.
