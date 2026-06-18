# sources/test-tools/fio/lib/pow2.h

Purpose: inline helper for power-of-two validation.

Important APIs/functions: `is_power_of_2(uint64_t val)` returns true for nonzero values with a single set bit.

Control flow/state: pure bit test `(val & (val - 1)) == 0` with explicit nonzero guard.

Dependencies/integration: includes fixed-width integers and fio bool definitions. Used by option validation and alignment/math code.

Risks/test signals: none beyond type width. Tests should cover zero, one, powers of two, and adjacent non-powers.
