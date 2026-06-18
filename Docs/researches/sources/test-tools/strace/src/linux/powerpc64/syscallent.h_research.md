<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent.h -->
# sources/test-tools/strace/src/linux/powerpc64/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for powerpc64 to strace decoder metadata. It contains about 278 explicit table entries and then composes shared rows through includes such as "syscallent-common.h", "../64/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	TD|TFSF|TSFA,	SEN(fstatfs),			"fstatfs"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `powerpc64` strace backend. It has SHA-1 prefix `7c35a33e4218`, 404 lines, and 20382 bytes. Key local interface signals: includes "syscallent-common.h", "../64/subcallent.h"; defines SYS_socket_subcall; 278 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "syscallent-common.h", "../64/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/syscallent.h -->
