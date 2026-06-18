# sources/test-tools/stress-ng/core-asm-openrisc.h

Purpose: OpenRISC synchronization instruction wrappers.

Important APIs and control flow: conditionally exposes `stress_asm_openrisc_msync` and `stress_asm_openrisc_psync` under `STRESS_ARCH_OR1K`.

State and persistence: no state; affects memory/pipeline synchronization.

Dependencies and integration: used by cache/memory fence shims and architecture-specific stressors.

Risks and test signals: requires correct assembler support macros. Signal is OpenRISC build coverage.
