# `sources/test-tools/fio/blktrace.h`

Purpose: Declares fio’s blktrace replay interface and cursor state, with stubbed no-op implementations when blktrace support is unavailable.

Important APIs and types: Under `FIO_HAVE_BLKTRACE`, `struct blktrace_cursor` tracks a trace file, current `blk_io_trace`, trace length, endian swap flag, scalar percentage, current iteration, and iteration count. Exported functions are `is_blktrace()`, `init_blktrace_read()`, `read_blktrace()`, and `merge_blktrace_iologs()`. Without support, static inline stubs return false.

Control flow and integration: Included by iolog/init code that needs to detect or replay binary block traces. Conditional compilation lets non-Linux/non-blktrace builds compile without the implementation.

State and persistence: Cursor state is transient during merge. Replay state is stored in `thread_data` by `blktrace.c`.

Dependencies: Requires `<asm/types.h>` and `blktrace_api.h` when enabled, plus fio `thread_data` declarations from surrounding includes.

Risks and test signals: Stub `merge_blktrace_iologs()` returns `false` as an `int`, which is zero/success-like and should match caller expectations carefully. Tests should compile both with and without `FIO_HAVE_BLKTRACE`.
