# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_kubsan.c

## Role

Provides OpenBSD kernel handlers for Clang undefined-behavior sanitizer callbacks. It records sanitizer events, rate/batch processes them via timeout, formats readable diagnostics, and optionally enters DDB.

## Key Behavior

- Defines ABI-compatible UBSan data structures for source locations, type descriptors, overflow, bounds, nullability, pointer overflow, shift, type mismatch, invalid value, and unreachable reports.
- `__ubsan_handle_*()` entry points convert compiler sanitizer callbacks into a compact `kubsan_report`.
- `kubsan_init()` allocates a fixed report array during boot and starts periodic reporting.
- `kubsan_defer_report()` suppresses duplicate source locations using a high bit in `sl_line`, reserves one of 32 slots atomically, and copies the report.
- `kubsan_report()` drains report slots, formats diagnostics per sanitizer kind, handles newly arrived reports, and reschedules itself.
- `kubsan_format_int()`, integer deserializers, shift helpers, and `kubsan_kind()` convert ABI-encoded values into readable messages.
- `kubsan_format_location()` and `pathstrip()` shorten absolute build paths to paths beginning after `/sys/`.
- `kubsan_unreport()` clears the reported bit when no report slot was available, allowing a future report attempt.

## Interfaces And Dependencies

Uses OpenBSD atomics, timeout scheduling, early boot page allocation, optional DDB entry, kernel printing, and Clang UBSan runtime symbol names.

## Notes

The implementation deliberately does not abort on undefined behavior. Reports are lossy under bursts because there are only 32 slots, but duplicate-location suppression reduces repeated noise.
