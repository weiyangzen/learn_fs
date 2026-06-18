# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ubsan.c

## Purpose
Provides a compact Undefined Behavior Sanitizer runtime for FreeBSD kernel builds and shared userland/libc use, defining the compiler-emitted `__ubsan_handle_*` entry points and formatting diagnostics for undefined behavior reports.

## Key Interfaces
- Public UBSan handlers cover integer overflow, negation, division/remainder overflow, shift errors, type mismatch, VLA bounds, out-of-bounds indexes, invalid values, invalid builtins, unreachable/missing return, function type mismatch, CFI failures, dynamic type cache misses, float cast overflow, nonnull/nullability violations, pointer overflow, and alignment assumptions.
- Abort variants call the same handlers with fatal reporting.
- `__ubsan_vptr_type_cache` is provided for C++ dynamic type instrumentation.
- `__ubsan_get_current_report_data()` is present but intentionally unimplemented.

## State And Locking
The only shared suppression state is embedded in compiler-provided source-location metadata: `isAlreadyReported()` atomically sets `ACK_REPORTED` in the location line field so each instrumented source location reports once. Userland builds also cache output policy in `ubsan_flags`, initialized from `LIBC_UBSAN`. There are no kernel locks in the report path.

## Control Flow
Each compiler handler validates metadata, delegates to a typed `Handle*()` routine, deserializes source location and operand/type data, suppresses duplicate reports for the same source location, and calls `Report()`. Kernel `Report()` uses `vpanic()` for fatal reports and `vprintf()` for recoverable reports. Userland `Report()` can print to stdout, stderr, syslog, and optionally abort based on `LIBC_UBSAN`.

## Integration Notes
The runtime understands Clang/GCC UBSan metadata layouts for integer and floating types, source locations, CFI records, alignment assumptions, and type-check kinds. Kernel builds reject unexpected floating operand decoding by fatal report. The code is intentionally portable between kernel and userland, with NetBSD-origin compatibility macros adapted for FreeBSD.

## Risks
Duplicate suppression mutates the compiler's source-location line field, so consumers must mask `ACK_REPORTED` when formatting. Some handlers are minimal or unimplemented, notably dynamic type cache miss and current-report data. Several abort wrapper functions delegate with nonfatal flags in this implementation, which is important to preserve or review carefully if aligning with upstream sanitizer behavior. Report paths must remain safe in early boot, interrupt-adjacent, and sanitizer-triggered contexts.
