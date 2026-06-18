# sources/test-tools/stress-ng/stress-prefetch.c

Purpose: `stress-prefetch.c` implements the `prefetch` stressor, benchmarking memory read throughput with no prefetch and many software/architecture-specific prefetch distances and methods.

Important APIs/types/functions: `stress_prefetch_info_t` records offset, count, duration, bytes, and rate for each tested distance. `stress_prefetch_method_t` maps method names to numeric codes, availability probes, and whether prefetch-rate sanity should be checked. Methods include compiler builtin localities, x86 prefetch variants, PPC `dcbt`/`dcbtst`, and ARM `prfm` variants. `stress_prefetch_benchmark()` flushes cache, measures loop overhead, performs the read/prefetch loop, verifies checksum if requested, and updates stats.

Control flow: the stressor selects a method, checks CPU availability, determines L3 cache size from Linux CPU cache details or defaults, maps a buffer plus prefetch-offset slack, fills deterministic 64-bit data and checksum, initializes 128 cache-line offsets, synchronizes, and loops over all offsets. At shutdown it computes per-offset rates, finds the best offset, emits non-prefetch and best-read GB/s metrics, and in verify mode can fail if the best prefetch rate is slower than no prefetch where rate checking is enabled.

State and persistence behavior: state is a private anonymous data buffer and stack metrics array. CPU cache state is intentionally flushed and perturbed. No files are written.

Dependencies and integration points: architecture asm helpers, CPU feature/cache detection, cache flush helper, builtin prefetch shim, stress-ng option parsing, metrics, and `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY` registration with optional verification.

Risks: performance comparisons are noisy and hardware-dependent; the verify rate check is enabled broadly on x86-64 and may be sensitive to virtualization, CPU frequency changes, or cache topology detection. Prefetch availability probes must match actual instruction support to avoid illegal instructions. Offset slack prevents prefetch pointers from running beyond the mapping.

Test signals: `--prefetch` should report non-prefetch and best-read GB/s metrics plus debug best offset. Variants should cover each available `--prefetch-method`, explicit `--prefetch-l3-size`, verify checksum mode, CPUs without a requested instruction, and systems without L3 cache info.
