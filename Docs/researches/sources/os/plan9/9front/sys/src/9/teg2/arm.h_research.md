# File Research: sources/os/plan9/9front/sys/src/9/teg2/arm.h

ARMv7/Cortex-A8/A9 shared constants for C and assembler. It defines PSR mode/status bits, coprocessor numbers and CP15 register selectors, system control bits, auxiliary-control bits, cache/TLB operation selectors, vector-base selectors, PL310-related control bits, ARMv7 L1/L2 PTE formats, access permissions, domains, cacheability/sharability attributes, and high-vector address.

The PTE comments emphasize that lock-containing memory must be cached, buffered, sharable, and write-allocate for LDREX/STREX to work in SMP mode.
