<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/syscallent.h -->
# sources/test-tools/strace/src/linux/riscv64/syscallent.h

## Purpose

This syscall table maps numeric Linux syscall slots for riscv64 to strace decoder metadata. It contains about 1 explicit table entries and then composes shared rows through includes such as "../64/syscallent.h". The table starts with entries like `[259] = { 3,	TM,		SEN(riscv_flush_icache),	"riscv_flush_icache"	},` and ends with entries like `[259] = { 3,	TM,		SEN(riscv_flush_icache),	"riscv_flush_icache"	},`, which is useful when checking generated row order. RISC-V adds `riscv_flush_icache` at syscall 259 after importing the generic 64-bit syscall table.

## Important APIs, Types, And Functions

This source is classified as `syscall-table` for the `riscv64` strace backend. It has SHA-1 prefix `f8d49cf186ab`, 11 lines, and 301 bytes. Key local interface signals: includes "../64/syscallent.h"; 1 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/syscallent.h" strace syscall decoder table macros. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are numeric table drift against kernel syscall headers, wrong argument count/flags, and mismatched compat table selection; failures appear as wrong syscall names or decoder dispatch. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/syscallent.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/syscallent.h -->
