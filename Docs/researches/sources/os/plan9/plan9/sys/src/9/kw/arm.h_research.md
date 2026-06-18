# File Research: sources/os/plan9/plan9/sys/src/9/kw/arm.h

## Purpose
Defines ARM processor status bits, CP15 register encodings, cache/TLB operation constants, Sheeva/Kirkwood L2 test/config registers, and MMU page-table permission/cache bits.

## Key Contents
- Program status register mode and flag constants such as `PsrMusr`, `PsrMirq`, `PsrMsvc`, `PsrDirq`, `PsrDfiq`, and condition flags.
- Coprocessor numbers and CP15 primary/secondary register selectors.
- CP15 control bits for MMU, alignment, data/instruction cache, write buffer, endian mode, permissions, and high vectors.
- Cache, TLB, and L2 test/config operation constants used by assembly and dynamic CP15 helpers.
- ARM page-table entry constants for L1/L2 mappings, cache/bufferability, domains, access permissions, and `HVECTORS`.
- PHY-facing helper register constants are not here; those are in `ethermii.h`.

## Dependencies and Integration
Used by ARM assembly, coprocessor access helpers, cache/MMU setup, exception handling, and platform initialization.

## Risks and Notes
The constants target pre-v7 ARM/ARM926EJ-S behavior, including implementation-defined `Mbo` and Sheeva-specific L2 control registers.
