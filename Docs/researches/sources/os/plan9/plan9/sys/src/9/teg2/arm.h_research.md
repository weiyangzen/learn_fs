# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arm.h

ARMv7/Cortex-A8/Cortex-A9 constants shared by Tegra C and assembly code.

Key contents:
- Defines ARM processor modes, PSR flags, mode masks, and bits that must remain zero.
- Defines coprocessor numbers and CP15 register/opcode names for ID, control, TTB, DAC, fault status/address, cache, TLB, lockdown, vector base, PID, and Cortex diagnostic registers.
- Defines CP15 control-register bits, Cortex-A9 auxiliary-control bits, cache/TLB maintenance operation encodings, performance-counter registers, and PL310 L2 auxiliary bits.
- Defines ARMv7 MMU L1/L2 PTE formats, access permissions, domain encodings, cacheability/shareability attributes, high-vector address, and helper macros for AP/DAC fields.

Role:
- This is the central CP15/MMU/cache ABI for startup assembly, `coproc.c`, MMU code, trap vectors, cache maintenance, and board reset.
- It encodes the port's requirement that memory containing locks be cached, buffered, write-allocate, and shareable so `LDREX`/`STREX` work correctly.

Notable constraints:
- Comments distinguish ARMv7-preferred permission encodings from older forms.
- Many definitions are Cortex-specific, not generic to all ARM versions.
