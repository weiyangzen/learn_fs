# sources/test-tools/stress-ng/core-asm-ppc64.h

Purpose: PowerPC/PPC64 inline wrappers for random number, cache, sync, and thread-priority hint instructions.

Important APIs and control flow: defines register-prefix handling for Apple/non-Apple assemblers; exposes PPC64 `darn`, `dcbst`, `dcbt`, `dcbtst`, `icbi`, `msync`, and PPC/PPC64 yield/mdoio/mdoom hint wrappers.

State and persistence: no durable state; instructions may flush/invalidate cache lines, sync memory, or influence hardware scheduling hints.

Dependencies and integration: used by cache flush/fence helpers and stressors needing PPC-specific instructions; gated by `STRESS_ARCH_PPC*` and `HAVE_ASM_PPC*` macros.

Risks and test signals: inline assembly constraints are architecture/compiler sensitive, especially register prefixes. Signal is successful PPC and PPC64 compilation plus stressor runtime coverage.
