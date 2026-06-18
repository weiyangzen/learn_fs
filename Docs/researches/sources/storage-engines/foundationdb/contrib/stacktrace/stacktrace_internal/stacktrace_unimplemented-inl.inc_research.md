# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_unimplemented-inl.inc

## Purpose
This file is the explicit no-op stack unwinder for unsupported platforms or builds where stack unwinding is intentionally disabled, such as selected Apple, Android, Native Client, Fuchsia, MIPS, or no-frame-pointer configurations.

## Important APIs, Types, And Functions
It defines `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` with the common signature and no stack inspection. It sets `*min_dropped_frames` to 0 when provided and returns 0 captured frames.

## Control Flow
There is no frame walk. All parameters except `min_dropped_frames` are ignored.

## State And Persistence
No state is kept.

## Dependencies And Integration Points
It exists solely to satisfy the stacktrace implementation contract for unsupported configurations selected by `ABSL_STACKTRACE_INL_HEADER`.

## Risks
Any platform routed here silently loses stacktrace data. That may be acceptable for unsupported targets but can mask accidental build-flag regressions, especially `NO_FRAME_POINTER` on architectures where no alternate unwinder is configured.

## Test Signals
Tests should verify calls return zero frames without crashing and that higher-level crash/logging code handles empty traces gracefully. Build-configuration tests should confirm only intended platforms select this file.
