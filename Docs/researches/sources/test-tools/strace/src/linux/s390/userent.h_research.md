<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent.h -->
# sources/test-tools/strace/src/linux/s390/userent.h

## Purpose

This user-area translation table exposes `struct user` register offsets for s390. It uses `XLAT`, `XLAT_UOFF`, or register-size macros so strace can print `PTRACE_PEEKUSER` offsets symbolically. It composes additional generic or compatibility fields through "userent0.h", "userent1.h".

## Important APIs, Types, And Functions

This source is classified as `userent-table` for the `s390` strace backend. It has SHA-1 prefix `cacb85bf0d55`, 42 lines, and 1131 bytes. Key local interface signals: includes "userent0.h", "userent1.h".

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "userent0.h", "userent1.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/userent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/userent.h -->
