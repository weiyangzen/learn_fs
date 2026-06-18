# File Research: sources/os/bsd/netbsd-src/sys/sys/ras.h

Read completely: 134 lines.

This header defines NetBSD restartable atomic sequences, or RAS, for userland and kernel consumers. It exposes `struct ras`, control operations `RAS_INSTALL`, `RAS_PURGE`, and `RAS_PURGE_ALL`, plus the userland `rasctl(void *, size_t, int)` interface.

For user code it provides declaration, address, size, and assembly-label macros: `RAS_DECL`, `RAS_START`, `RAS_END`, `RAS_ADDR`, `RAS_SIZE`, and assembly variants including hidden-symbol forms. Kernel code gets `ras_lookup`, `ras_fork`, and `ras_purgeall`.

Important behavior: the C macros emit global labels with compiler memory barriers, but the comments strongly prefer assembly-authored RAS regions because compiler-generated C may not be safely restartable.

Risks: correctness depends on exact instruction ranges and restart-safe machine code. ABI exposure is through symbol labels and `rasctl`, so label visibility and range sizing mistakes can break atomicity.
