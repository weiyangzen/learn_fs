# sources/test-tools/strace/src/linux/x32/arch_fpregset.c

## Purpose
Reuses the x86_64 floating-point register-set decoder for the x32 target.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_fpregset.c`, which defines `arch_decode_fpregset` for non-`MPERS_IS_m32` builds and delegates to i386 for m32 builds.

## Control Flow and Integration
The inherited decoder validates size alignment, fetches up to `sizeof(struct_fpregset)` from tracee memory with `umoven_or_printaddr`, prints x87/SSE control fields and arrays progressively by fetched size, and indicates extra data when the kernel-provided size is larger than known layout.

## State and Persistence
No persistent state. It reads tracee memory and writes formatted output.

## Dependencies
Depends on x86_64 `arch_fpregset.h`, `struct_fpregset`, generic regset decoding, and i386 mpers support when compiled for m32.

## Risks
The x32 ABI shares x86_64 kernel register layouts even though user long size is 32-bit. The include indirection is correct only if x32 regset layout remains x86_64-compatible.

## Test Signals
Regset tests for `NT_FPREGSET` on x32 should decode control words, `st_space`, `xmm_space`, padding, malformed sizes, and oversized buffers.
