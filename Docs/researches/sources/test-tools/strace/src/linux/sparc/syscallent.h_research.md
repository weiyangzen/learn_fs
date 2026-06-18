<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/syscallent.h -->
# sources/test-tools/strace/src/linux/sparc/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for sparc to strace decoder metadata. It contains about 275 explicit table entries and then composes shared rows through includes such as "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h". It defines `SYS_socket_subcall` as 500 before including the socket subcall table, so old multiplexed socket calls occupy the architecture-specific extension range expected by strace. The table starts with entries like `[100] = { 2,	0,		SEN(getpriority),		"getpriority"		},` and ends with entries like `[402] = { 3,	TI,		SEN(msgctl),			"msgctl"		},`, which is useful when checking generated row order.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `sparc` strace backend. It has SHA-1 prefix `67735ee54bdb`, 389 lines, and 19881 bytes. Key local interface signals: includes "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h"; defines SYS_socket_subcall; 275 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../32/syscallent-common-32.h", "syscallent-common.h", "../32/subcallent.h" Linux ptrace regset APIs strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/syscallent.h -->
