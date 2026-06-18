# sources/test-tools/stress-ng/core-arch.h

Purpose: central compile-time architecture and endian detection header.

Important APIs and control flow: defines `STRESS_ARCH_*`, `STRESS_ARCH_LE/BE`, `STRESS_ARCH_X86`, opcode sizes and masks, and declares `stress_arch_get`. It also disables `HAVE_SIGALTSTACK` on HPPA.

State and persistence: compile-time macro state only.

Dependencies and integration: included by architecture assembly wrappers, CPU probes, cache helpers, and opcode generation.

Risks and test signals: detection relies on compiler predefined macros; ordering matters for PPC64 before PPC and x86 variants. Signal is correct conditional compilation on every supported architecture.
