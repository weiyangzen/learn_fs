# sources/test-tools/stress-ng/stress-vm.c

## Purpose
Implements the main `vm` anonymous virtual-memory stressor. It allocates per-worker memory and runs a large catalog of memory algorithms to stress RAM, cache, TLBs, page residency, NUMA placement, non-temporal/direct stores, vector writes, rowhammer-like access, and data verification.

## Important APIs, types, and functions
`stress_vm()` is the registered entry point and `stress_vm_child()` runs the mmap/method loop in an OOM-managed child. `stress_vm_func` is the common method signature; `stress_vm_method_info_t` maps names to methods; `stress_vm_context_t` carries selected method, shared bit-error count, NUMA masks, byte size, mmap stats, and mmap/munmap timings. Methods include moving inversion, modulo-X, walking data/address, gray/grayflip, incdec, prime-step operations, random set/sum, rotate/flip, one-zero/zero-one, galloping patterns, nybble increment, read/write64, direct/non-temporal stores, vector writes, rowhammer, mscan, cache line/stripe, fwdrev, LFSR32, checkerboard, and `all`.

## Control flow
`stress_vm()` allocates shared context and a shared bit-error page, discovers cache-line size, resolves NUMA/method/options, scales `vm-bytes` by instance count, synchronizes, and invokes `stress_oomable_child()`. `stress_vm_child()` reads flags, maps or reuses an anonymous buffer, applies populate/madvise/NUMA/discontiguous behavior, touches pages, calls the selected method, optionally sleeps for `vm-hang`, gathers mmap stats, and unmaps unless `vm-keep` is active. The `all` method rotates through every real method.

## State and persistence
State is process-local plus anonymous shared mappings for context and bit-error count. Static method variables intentionally vary offsets and patterns across passes. No files persist. Bogo operations are internally shifted by `VM_BOGO_SHIFT` and reduced before final reporting.

## Dependencies and integration points
Registered as `stress_vm_info` with `CLASS_VM | CLASS_MEMORY | CLASS_OS`, options for bytes, discontiguous mappings, flush, hang, keep, locked, madvise, method, NUMA, and populate, and `VERIFY_OPTIONAL`. It depends on stress-ng mmap/madvise/mincore/cache/NUMA/OOM/signal/metric helpers and optional architecture helpers for x86 direct stores, non-temporal loads/stores, vectors, and 128-bit operations.

## Risks and edge cases
The stressor intentionally consumes memory and shrinks `buf_sz` after repeated `ENOMEM`. `vm-hang 0` can sleep indefinitely until stopped. Hardware-sensitive paths include rowhammer, cache flush, direct stores, and non-temporal stores. A probable metric typo reports `munmaps total` using `context->mmap_count` rather than `context->munmap_count`. Bit errors force failure when the shared counter is nonzero.

## Test signals
Signals include per-method bit-error reports, final `detected ... bit errors` failure, mmap/munmap timing metrics, mmap residency/dirty/swap/contiguity stats, resource skips, and method-selection debug output.
