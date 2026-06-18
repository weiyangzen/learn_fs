# File Research: sources/os/linux/linux/mm/kmsan/report.c

## Role

KMSAN reporting implementation. It formats bug reports, decodes origin chains from stack depot, serializes report output, and optionally panics on reports.

## Global State

- `kmsan_report_lock` serializes report formatting.
- `report_local_descr` is a fixed buffer for local variable descriptions.
- `panic_on_kmsan` is exported and exposed as module parameter `kmsan.panic`.

## Stack Filtering

- `get_stack_skipnr()` skips internal `__msan_*` and `kmsan_*` frames so reports point at user/kernel code of interest.
- It formats symbols into a small buffer and stops at the first non-runtime frame.

## Origin Formatting

- `pretty_descr()` converts Clang local descriptions like `----local@function` into a cleaner local variable name.
- `kmsan_print_origin()` decodes stack-depot records:
  - alloca origins identify a local variable and creation PCs.
  - chain origins show where uninitialized data was stored, then continue to the previous origin.
  - ordinary origins print the creation stack.
- Chained origins at maximum depth print a truncation notice.
- Fetched chained stack entries are unpoisoned before printing.

## Report Emission

`kmsan_report()`:

- Returns early when KMSAN is disabled, already in runtime, disabled for the current task, or missing an origin.
- Enters runtime, saves user-access state, and takes the report lock.
- Determines bug type from reason and origin UAF bit:
  - `uninit-value`
  - `use-after-free`
  - `kernel-infoleak`
  - `kernel-infoleak-after-free`
  - `kernel-usb-infoleak`
  - `kernel-usb-infoleak-after-free`
- Captures and prints the current stack after skipping runtime frames.
- Prints the origin chain.
- Prints byte-range, access address, and user-copy destination details when available.
- Adds `TAINT_BAD_PAGE` with unreliable lockdep state.
- Panics when `panic_on_kmsan` is set.

## Dependencies

Uses console/module parameters, stack depot, stack trace printing, user access save/restore, raw spinlocks, and KMSAN core helpers.

## Research Notes

This file is focused on producing useful and non-recursive reports. The raw spinlock plus runtime guard prevents report interleaving and sanitizer recursion, while stack filtering and origin-chain decoding make reports actionable.
