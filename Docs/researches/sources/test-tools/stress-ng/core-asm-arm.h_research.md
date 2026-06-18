# sources/test-tools/stress-ng/core-asm-arm.h

Purpose: ARM/AArch64 inline assembly wrappers for prefetch, yield, and memory barrier instructions.

Important APIs and control flow: conditionally defines `stress_asm_arm_prfm_*`, `stress_asm_arm_yield`, and `stress_asm_arm_dmb_sy` only when ARM architecture and feature probes are present.

State and persistence: no persistent state; operations affect CPU pipeline/cache ordering.

Dependencies and integration: relies on `core-arch.h`, `core-attribute.h`, and `HAVE_ASM_ARM_*` generated config macros.

Risks and test signals: invalid feature detection can cause assembler failures or illegal instructions. Signal is per-architecture compilation and successful stressors using prefetch/barrier helpers.
