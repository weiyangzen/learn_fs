<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h

## Purpose

This file is a one-line architecture wrapper that includes "../64/ioctls_inc.h". It intentionally has no local control flow; the selected include target supplies the real implementation for this personality or endian variant.

## Important APIs, Types, And Functions

This source is classified as `include-wrapper` for the `riscv64` strace backend. It has SHA-1 prefix `3defd9a34cb2`, 1 lines, and 30 bytes. Key local interface signals: includes "../64/ioctls_inc.h".

## Control Flow

At compile time the preprocessor substitutes the referenced implementation or table into this architecture directory. Runtime behavior is therefore the behavior of the included file under this ABI selection.

## State And Persistence Behavior

The file has no mutable state or persistence; it contributes static compile-time data or a preprocessor include edge.

## Dependencies And Integration Points

preprocessor includes: "../64/ioctls_inc.h". The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is include-target drift: if the shared file changes assumptions about word size, endian, or personality, this wrapper silently inherits that behavior. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/ioctls_inc0.h -->
