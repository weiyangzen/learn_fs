# sources/test-tools/fio/lib/zipf.c

Purpose: implements Zipf and Pareto non-uniform random distributions for fio range selection.

Important APIs/functions: `zipf_init`, `zipf_next`, `pareto_init`, `pareto_next`, and `zipf_disable_hash`. Static `zipf_update` computes the zeta normalization up to `min(nranges, 10M)`, and `shared_rand_init` seeds common state and center offset.

Control flow: Zipf init stores theta/zeta constants and precomputes normalization. `zipf_next` draws a uniform random value, maps it through Zipf equations, optionally hashes it, adds a random or centered offset, and mods by `nranges`. Pareto uses a precomputed exponent from `h` and similar hash/offset mapping.

State/persistence: mutable `zipf_state` contains distribution parameters, RNG state, offset, and hash-disable flag. No heap allocation.

Dependencies/integration: depends on `math.h`, fio RNG, hash, and min macros. Used by random workload distribution options.

Risks/test signals: `nranges == 0`, invalid theta/h, or extreme values can cause division/modulo issues. The 10M cap trades accuracy for startup time. Tests should check bounds, determinism, center behavior, hash disable behavior, and rough distribution shape.
