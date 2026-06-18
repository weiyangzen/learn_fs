<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/sh/ioctls_arch0.h

## Purpose

This generated ioctl table records 76 architecture-local ioctl definitions for sh, with header names, symbolic names, `_IOC_*` direction, request numbers, and encoded argument sizes. Boundary rows include `{ "asm/ioctls.h", "FIOASYNC", _IOC_WRITE, 0x667d, 0x04 },` and `{ "mach-landisk/mach/gio.h", "GIODRV_IOCSGIOSETADDR", _IOC_WRITE, 0x6b07, 0x04 },`, showing the source header family and final request preserved by generation.

## Important APIs, Types, And Functions

This source is classified as `ioctl-arch-table` for the `sh` strace backend. It has SHA-1 prefix `08fef056b41e`, 77 lines, and 4643 bytes. Key local interface signals: 76 table rows.

## Control Flow

There is no executable control flow. The strace build includes this data into generated lookup arrays; runtime lookup indexes by syscall number, ioctl request, errno, signal, or user offset and then dispatches to generic printers/decoders.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

Linux ioctl encoding macros and generated `ioctls_gen.sh` output. The integration point is strace's per-architecture Linux backend under `src/linux/sh`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Risks are stale generated ioctl metadata, request-size mismatches between 32-bit and 64-bit personalities, and duplicate request numbers resolving to the wrong symbolic name. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compare generated tables with current kernel headers and run decoder lookup tests for representative low, high, compat, and architecture-specific numbers. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh/ioctls_arch0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh/ioctls_arch0.h -->
