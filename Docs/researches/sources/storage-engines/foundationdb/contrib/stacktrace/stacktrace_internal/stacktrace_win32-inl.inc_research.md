# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace_internal/stacktrace_win32-inl.inc

## Purpose
This file implements Windows stack capture using the undocumented but common `RtlCaptureStackBackTrace` exported by `ntdll.dll`. It avoids heavier symbol-server or `StackWalk64` dependencies.

## Important APIs, Types, And Functions
`RtlCaptureStackBackTrace_Function` declares the Windows function type. `RtlCaptureStackBackTrace_fn` is resolved at static initialization with `GetProcAddress(GetModuleHandleA("ntdll.dll"), "RtlCaptureStackBackTrace")`. `UnwindImpl<IS_STACK_FRAMES, IS_WITH_CONTEXT>` calls it with `skip_count + 2`, copies up to `max_depth`, zeroes frame sizes when requested, and does not implement dropped-frame counting.

## Control Flow
If the function pointer is unavailable, the implementation returns zero frames. Otherwise Windows fills the caller-provided result buffer directly. `ucp` is ignored.

## State And Persistence
The only state is the static function pointer resolved at load time. There is no persistence.

## Dependencies And Integration Points
It depends on `windows.h`, `ntdll.dll`, and the stacktrace common template signature. It is selected by `_WIN32`.

## Risks
The comment notes frame-pointer optimization can make Windows traces difficult; `RtlCaptureStackBackTrace` may not fully handle FPO. Static initialization touches loader-provided functions, which is intentional here to avoid later loader-lock issues. Frame sizes and dropped-frame lower bounds are unavailable.

## Test Signals
Windows tests should cover debug and release builds, missing/failed symbol resolution behavior, depth/skip semantics, zeroed frame sizes, and caller behavior with `min_dropped_frames == 0`.
