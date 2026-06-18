# sources/test-tools/stress-ng/core-asm-loong64.h

Purpose: LoongArch64 inline wrappers for time counter, data barrier, and CPU config instructions.

Important APIs and control flow: provides `stress_asm_loong64_rdtime`, `stress_asm_loong64_dbar`, and `stress_asm_loong64_cpucfg` when corresponding feature macros exist.

State and persistence: no durable state; reads CPU state and applies memory ordering.

Dependencies and integration: depends on Loong64 architecture detection and generated assembler capability macros.

Risks and test signals: incorrect endian/assembler feature assumptions can break builds or runtime. Signal is Loong64-specific compile and stressor execution.
