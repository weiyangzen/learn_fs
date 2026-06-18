# sources/test-tools/stress-ng/core-asm-ret.h

Purpose: declares the return-opcode data structure and support check.

Important APIs and control flow: defines `stress_ret_opcode_t`, `stress_ret_func_t`, global `stress_ret_opcode`, and `stress_asm_ret_supported`.

State and persistence: no header state; consumers read the global opcode constant from `core-asm-ret.c`.

Dependencies and integration: integrates generated executable code stressors with architecture opcode selection.

Risks and test signals: consumers must respect `len` and `stride` and call support checks. Signal is compile-time ABI compatibility and runtime code-generation tests.
