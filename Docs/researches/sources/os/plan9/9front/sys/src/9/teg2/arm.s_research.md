# File Research: sources/os/plan9/9front/sys/src/9/teg2/arm.s

Assembler macro/header file for Tegra 2 ARM code. It defines address conversion macros, L1 PTE construction helpers, early delay and UART byte-output macros, raw instruction encodings for ARMv7/TrustZone/barrier/FP operations, cache/TLB barrier sequences, PTE fill/zero macros, zero-segment static-base setup, ARMv7 RFE encodings, and CPU-ID extraction.

This file is included by low-level assembly such as startup, exception, cache, and reboot code. It encodes assumptions about R9/R10 register globals and avoids R11 due to loader use.
