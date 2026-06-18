<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/s390/ioctls_arch0.h

## Purpose

This generated ioctl table records 185 architecture-local ioctl definitions for s390, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/chsc.h", "CHSC_INFO_CCL", _IOC_READ|_IOC_WRITE, 0x6386, 0x1014 },` and `{ "linux/kvm.h", "KVM_UNREGISTER_COALESCED_MMIO", _IOC_WRITE, 0xae68, 0x10 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `s390` strace backend. It has SHA-1 prefix `caab416b16d6`, 186 lines, and 12702 bytes. Key local interface signals: 185 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/ioctls_arch0.h -->
