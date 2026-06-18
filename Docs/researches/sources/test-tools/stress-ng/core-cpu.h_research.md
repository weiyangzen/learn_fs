# sources/test-tools/stress-ng/core-cpu.h

Purpose: declares CPU feature, DTLB, and floating-point mode helpers.

Important APIs and control flow: exposes x86 feature booleans, DTLB entry query, and subnormal enable/disable functions.

State and persistence: no header state, but implementations cache and mutate CPU/FP state as documented in `core-cpu.c`.

Dependencies and integration: included by cache, x86 stressors, and config checks.

Risks and test signals: consumers must gate instruction use with the matching helper. Signal is compile/link and absence of illegal-instruction failures when used correctly.
