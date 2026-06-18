# File Research: sources/os/linux/linux/mm/kasan/report.c

## Role

Common KASAN error-reporting implementation. It handles report throttling, KUnit integration, report suppression, report locking, error formatting, address/object/page descriptions, memory metadata dumps, and dispatch for access, invalid-free, and asynchronous hardware-tag reports.

## Key Behavior

- Parses `kasan.fault=report|panic|panic_on_write` and `kasan_multi_shot`.
- Enforces single-shot reporting unless multi-shot is enabled; KASAN KUnit tests can temporarily enable multi-shot.
- Suppresses reports during KASAN-disabled critical sections for software modes, while hardware tag mode suppresses CPU tag checks around report printing.
- `start_report()` disables trace-on-warning, disables lockdep, suppresses recursive KASAN checking, takes `report_lock`, and prints the report banner.
- `end_report()` emits trace end events, unlocks, honors `panic_on_warn` and `kasan.fault`, taints the kernel, restores lockdep, and re-enables checking.
- `complete_report_info()` identifies first bad address, slab/cache/object metadata, allocation size, invalid/double-free type, and calls the mode-specific completion hook.
- `print_report()` prints bug type, pointer/memory tags when available, stack trace, slab object allocation/free stacks, variable/global/stack/vmalloc/page descriptions, and surrounding metadata.
- `kasan_report()` wraps regular access reports with `user_access_save/restore`.
- `kasan_report_invalid_free()` reports invalid and double free without software-suppression checks.
- `kasan_report_async()` handles hardware tag asynchronous faults with no address details.
- `kasan_non_canonical_hook()` decodes shadow faults from bogus pointers into null/user/wild-memory-access hints.

## Dependencies

Uses KUnit, stack depot, stack trace, slab internals, vmalloc, module address checks, task stack helpers, KASAN mode hooks from `kasan.h`, and `trace/events/error_report.h`.

## Research Notes

This file is the shared presentation and policy layer for KASAN reports. It deliberately disables instrumentation and lockdep while reporting to avoid recursive faults or deadlocks, then delegates mode-specific classification and metadata decoding to `report_generic.c`, `report_tags.c`, `report_sw_tags.c`, or `report_hw_tags.c`.
