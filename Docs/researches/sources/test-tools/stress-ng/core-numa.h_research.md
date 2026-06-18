# sources/test-tools/stress-ng/core-numa.h

Purpose: public NUMA support contract and fallback memory-policy constants.

Important APIs/types: `stress_numa_mask_t`, missing `MPOL_*` and `MPOL_F/MF_*` constants, and declarations for all NUMA helper functions.

Control flow: no header runtime flow. Constants allow compilation on headers lacking newer memory-policy values.

State/persistence: no header state; declared APIs may allocate masks, cache node counts, and set process memory policy.

Dependencies/integration: optionally includes `<linux/mempolicy.h>` and relies on common stress-ng types.

Risks: fallback constants must match kernel ABI values; mask size fields can be misused because bits and bytes are both represented.

Test signals: old/new Linux header builds, mask allocation/free ownership, and callers clearing feature flags when allocation fails.
