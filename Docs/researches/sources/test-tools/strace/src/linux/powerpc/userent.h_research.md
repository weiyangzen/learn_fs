<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/userent.h -->
# sources/test-tools/strace/src/linux/powerpc/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for powerpc. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "userent0.h". The file defines or uses `REGSIZE` to keep offset arithmetic tied to the tracee word size rather than the host compiler default.

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `powerpc` strace backend. It has SHA-1 prefix `a8aad866bf68`, 54 lines, and 1403 bytes. Key local interface signals: includes "userent0.h"; defines PT_ORIG_R3, REGSIZE.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h". The integration point is strace's per-architecture Linux backend under `src/linux/powerpc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/userent.h -->
