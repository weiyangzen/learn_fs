# sources/test-tools/stress-ng/stress-x86cpuid.c

## Purpose
Implements x86-only `x86cpuid`, repeatedly executing a broad set of CPUID leaves/subleaves and verifying selected stable leaves for consistent output.

## Important APIs, types, and functions
`stress_x86cpuid()` is the entry point on x86. `stress_cpuid_regs_t` defines input `eax`, input `ecx`, and verify flag; `stress_cpuid_saved_regs_t` stores output registers. `stress_cpuid_regs[]` covers standard, extended, hypervisor, AMD, Centaur, Xeon Phi, topology, cache, RDT, SGX, AVX10, and related leaves. `stress_x86cpuid_reorder_regs()` randomizes execution order each pass.

## Control flow
After synchronization, each loop shuffles leaves, snapshots verified leaves, times 1024 sweeps over the shuffled list, then rechecks verified leaves against snapshots. Any register mismatch fails the run. On exit it reports nanoseconds per CPUID instruction.

## State and persistence
State is local shuffled arrays, saved register arrays, counters, timing, and return code. No persistent state is written.

## Dependencies and integration points
Registered as `stress_x86cpuid_info` with `CLASS_CPU` and `VERIFY_ALWAYS`. Depends on stress-ng x86 assembly wrappers and pragma unrolling. Non-x86 builds are unimplemented.

## Risks and edge cases
Some CPUID leaves can vary under virtualization, hotplug, topology, or firmware behavior, so only selected leaves are verified. Unusual vendor or hypervisor leaves may reveal emulation inconsistencies. Shuffling catches order-dependent CPUID bugs.

## Test signals
Failures log the leaf/subleaf and mismatched register values. Metric is `nanosecs per cpuid instruction`.
