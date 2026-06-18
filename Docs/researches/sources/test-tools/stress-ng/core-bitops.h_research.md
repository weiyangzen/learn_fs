# sources/test-tools/stress-ng/core-bitops.h

Purpose: inline bit-manipulation primitives with builtin fallbacks.

Important APIs and control flow: provides reverse-bit functions for 8/16/32/64, byte swap, popcount, parity, and next-power-of-two helpers. Builtins are preferred when available; otherwise portable bit-twiddling implementations are used.

State and persistence: pure/stateless inline computations.

Dependencies and integration: used by stressors and helpers needing deterministic bit operations; depends on `core-attribute.h` and builtin feature macros.

Risks and test signals: `stress_bitops_nextpwr2(0)` wraps through unsigned arithmetic; fallback correctness depends on width assumptions. Signals are unit-style stressor self-checks and compiler warnings under pedantic builds.
