# sources/test-tools/fio/lib/fls.h

Purpose: provides `__fls`, a 32-bit find-last-set helper.

Important APIs/functions: inline `__fls(int x)` returns 0 for input 0 and otherwise a 1-based index of the most significant set bit.

Control flow/state: pure bit manipulation using left shifts and decrementing an initial result of 32. No state or dependencies beyond the header guard.

Dependencies/integration: used by `roundup.h` to compute powers of two, and by any code needing generic bit operations without arch intrinsics.

Risks/test signals: takes `int`, so callers with wider unsigned values must not expect 64-bit behavior. Tests should cover 0, 1, high bit, and mixed-bit values.
