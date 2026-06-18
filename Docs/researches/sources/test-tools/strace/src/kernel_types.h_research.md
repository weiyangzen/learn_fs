# sources/test-tools/strace/src/kernel_types.h

Purpose: normalizes kernel long and 64-bit printf formatting types across architectures and personalities.

Important APIs/types/functions: `kernel_long_t`, `kernel_ulong_t`, fallback `__kernel_long_t`/`__kernel_ulong_t`, `PRI_kl*`, and `PRI__*64` format macros.

Control flow: preprocessor selects 64-bit kernel longs for MIPS n32 and x32, uses `<asm/posix_types.h>` when kernel typedefs are available, otherwise falls back to C `long`. It then derives printf length modifiers for kernel longs and kernel-exported 64-bit integer types.

State and persistence behavior: no runtime state; compile-time type/format contract.

Dependencies and integration points: foundational header for many ABI structs and numeric printers. The `PRI__64` selection matches Linux UAPI choices for ALPHA, IA64, powerpc64, MIPS64, Android exceptions, and 32-bit hosts.

Risks: wrong kernel-long sizing breaks pointer, length, and structure decoding across the tree. Format macros must match typedef choices to avoid undefined behavior in printf calls.

Test signals: build and run formatting tests on native 64-bit, 32-bit, x32, MIPS n32, and architectures using unsigned long for UAPI 64-bit fields.
