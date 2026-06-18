# sources/user-network-fs/libfuse/lib/usdt.h

## Purpose
Single-header USDT tracepoint macro library copied from libbpf. It lets code define low-overhead user statically-defined tracepoints, optional semaphores, and ELF note metadata consumable by BPF/SystemTap-style tracers.

## Important APIs, Types, And Functions
- `USDT(group, name, ...)` emits a semaphoreless probe.
- `USDT_WITH_SEMA`, `USDT_IS_ACTIVE`, `USDT_WITH_EXPLICIT_SEMA`, `USDT_DEFINE_SEMA`, `USDT_DECLARE_SEMA`, and `USDT_SEMA_IS_ACTIVE` provide implicit and explicit semaphore variants.
- `struct usdt_sema` stores a volatile 16-bit activity counter.
- Internal macros emit `.note.stapsdt`, `.stapsdt.base`, `.probes`, argument-size descriptors, and architecture-specific operand constraints.

## Control Flow
Macro expansion inserts a NOP at the callsite, emits note-section metadata with provider/name/argument operand descriptions, and optionally defines or references a hidden semaphore symbol. Runtime flow is effectively a NOP unless a tracer patches the site or updates semaphore state.

## State And Persistence
State lives in ELF sections and optional semaphore variables in `.probes`; there is no filesystem persistence. Semaphore activity is modified by tracing infrastructure and read by application code.

## Dependencies And Integration Points
Depends on compiler support for GNU-style inline assembly, `__builtin_classify_type`, variadic macros, and target-specific operand constraints. Compatible with BPF-based USDT tooling and SystemTap note format.

## Risks
The explicit/implicit semaphore macro definitions appear inverted around `__VA_OPT__` handling in the source snapshot: one branch uses `##__VA_ARGS__` under `__usdt_va_opt`, and the other uses `__VA_OPT__` when the feature is not defined. That should be compile-tested. Inline asm constraints can fail with complex or too many operands, and C++ signedness support relies on templates in a header.

## Test Signals
Compile C and C++ users with 0, 1, and many arguments; inspect ELF notes with tracing tools; attach bpftrace/SystemTap; test semaphore activation; build on i386, arm, powerpc, loongarch, and 64-bit targets.
