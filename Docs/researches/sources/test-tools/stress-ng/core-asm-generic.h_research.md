# sources/test-tools/stress-ng/core-asm-generic.h

Purpose: generic inline assembly no-op and compiler memory barrier helpers.

Important APIs and control flow: `stress_asm_nop` emits target no-op, with KVX bundle syntax and OpenRISC fallback; `stress_asm_mb` emits a compiler memory clobber; `stress_asm_nothing` emits empty asm.

State and persistence: none.

Dependencies and integration: included by stressors needing minimal instruction/pipeline effects; controlled by config macros.

Risks and test signals: assembly syntax must match target compiler; no-op semantics are intentionally minimal. Signal is compilation across supported compilers and expected use in microbenchmarks.
