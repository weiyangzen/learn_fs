# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_generic-inl.inc

## Purpose
This is the portable fallback unwinder that delegates to glibc `backtrace`. It is used where FoundationDB/Abseil chooses a generic implementation, notably PowerPC builds without frame pointers per the stacktrace config.

## Important APIs, Types, And Functions
The only implementation is `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>`. It allocates a fixed local stack array of 64 PCs, calls `backtrace`, skips the current frame plus requested frames, copies up to `max_depth`, zeroes frame sizes when requested, and computes a simple dropped-frame lower bound.

## Control Flow
The function ignores `ucp` and signal context. It uses `backtrace` output order directly, adjusts for `skip_count + 1`, clamps to caller depth, and returns the number copied.

## State And Persistence
There is no retained state. All output is written to caller-provided buffers.

## Dependencies And Integration Points
It depends on `<execinfo.h>` and glibc-compatible `backtrace`. It plugs into the same `UnwindImpl` template API as all architecture-specific unwinders.

## Risks
The file notes that glibc `backtrace` may call `malloc`, which can deadlock in heap profiling or crash-handler contexts. It cannot produce real frame sizes and cannot use signal context, so stack traces may be less reliable for the very paths stacktrace is often needed to debug.

## Test Signals
Basic stack depth tests are useful, but crash-safety and malloc-reentrancy are the important integration risks. Tests should also verify frame-size arrays are zero-filled and dropped-frame counts are non-negative.
