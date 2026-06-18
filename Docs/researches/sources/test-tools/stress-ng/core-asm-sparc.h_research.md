# sources/test-tools/stress-ng/core-asm-sparc.h

Purpose: SPARC tick and memory barrier wrappers.

Important APIs and control flow: conditionally defines `stress_asm_sparc_tick` and `stress_asm_sparc_membar`.

State and persistence: no durable state; reads hardware tick and enforces store-load ordering.

Dependencies and integration: used by timing and cache/memory fence paths.

Risks and test signals: feature macros must reflect assembler and CPU support. Signal is SPARC build and runtime coverage for fence/tick users.
