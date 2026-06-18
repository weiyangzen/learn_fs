# sources/storage-engines/foundationdb/contrib/stacktrace/stacktrace.amalgamation.cpp

## Purpose
This file is an amalgamated Abseil-derived stacktrace implementation used by FoundationDB's contrib stacktrace library. It packages public stack capture APIs, platform selection, low-level frame unwinders, readable-address probing, ELF/VDSO symbol lookup, and dynamic-annotation stubs into a single translation unit. Its primary public surface is `absl::GetStackFrames`, `absl::GetStackFramesWithContext`, `absl::GetStackTrace`, `absl::GetStackTraceWithContext`, `absl::SetStackUnwinder`, and `absl::DefaultStackUnwinder`.

## Important APIs, Types, And Functions
The top-level stack API dispatches through a file-local atomic `custom` unwinder. `SetStackUnwinder` installs a process-wide custom unwinder and `DefaultStackUnwinder` bypasses it. `ABSL_STACKTRACE_INL_HEADER` is selected by architecture and frame-pointer availability, mapping to the included `stacktrace_*` implementation. `absl::debug_internal::AddressIsReadable` probes arbitrary pointers without intentionally faulting; on Linux it uses a cached pipe and `syscall(SYS_write)` to test whether one byte can be read. `ElfMemImage` models in-memory ELF dynamic tables and exposes symbol iteration, `LookupSymbol`, and `LookupSymbolByAddress`. `VDSOSupport` locates the Linux VDSO from `/proc/self/auxv`, caches it in `vdso_base_`, resolves `__vdso_getcpu`, and exposes `GetCPU`.

## Control Flow
Stack capture calls enter `Unwind<IS_STACK_FRAMES, IS_WITH_CONTEXT>`, select either the default `UnwindImpl` template or a custom unwinder, adjust `skip_count`, and return captured PCs and optional frame sizes. Platform unwinders walk frame pointers or delegate to OS/glibc helpers. With signal context, supported unwinders use `ucontext_t` to recover pre-signal frame pointers. VDSO setup runs early through `VDSOInitHelper`, then later symbol lookups iterate ELF tables using dynamic-section pointers and version metadata.

## State And Persistence
Persistent state is process-local only: atomic custom unwinder, Linux readable-address pipe descriptors packed with the current pid, VDSO base cache, and cached getcpu function pointer. There is no file/database persistence. The Linux pipe probe can intentionally leak a small number of file descriptors across fork edge cases, which the comments treat as acceptable for crash-path usage.

## Dependencies And Integration Points
The file depends on compiler builtins, platform ABI frame layout, Linux `ucontext`, `link.h`, ELF dynamic tables, `/proc/self/auxv`, low-level syscalls, Windows `RtlCaptureStackBackTrace`, and optional sanitizer/Valgrind annotations. It integrates with FoundationDB where stack traces are needed without a wider Abseil dependency and with architecture-specific `.inc` files selected by preprocessor macros.

## Risks
Correctness is highly ABI-sensitive. Frame-pointer omission routes several platforms to the unimplemented or generic path, and the generic glibc path may allocate, which is risky in malloc/crash handlers. `SetStackUnwinder` is global and can race with threads still executing a previous unwinder. Some code uses `assert`/raw checks in low-level paths, so malformed ELF/VDSO state may abort in debug builds. The amalgamation must stay synchronized with its included architecture files and the public header.

## Test Signals
This file has no direct local test in the subset. Useful signals would be architecture-specific stack capture tests, signal-handler stack capture with `ucontext_t`, `max_depth == 0`, custom unwinder installation/removal, VDSO symbol lookup on Linux, and sanitizer/Valgrind builds.
