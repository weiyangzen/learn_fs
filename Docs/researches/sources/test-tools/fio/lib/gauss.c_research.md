# sources/test-tools/fio/lib/gauss.c

Purpose: produces pseudo-Gaussian-distributed offsets/ranges from fio's random generator.

Important APIs/functions: `gauss_init` and `gauss_next` are declared in the header; implementation initializes range, deviance, center, and seed state, then sums repeated uniform draws (`GAUSS_ITERS`) to approximate a normal distribution before mapping into `nranges`.

Control flow/state: initialization seeds an embedded `frand_state` and computes center offset. Each next call samples the RNG repeatedly, scales the result by deviance, hashes/offsets as needed, and returns a bounded range value.

Dependencies/integration: depends on `math.h`, fio hash helpers, and `rand.h`. It is part of fio's random distribution options alongside Zipf/Pareto.

Risks/test signals: statistical quality depends on `GAUSS_ITERS`, deviance parameters, and modulo mapping. Tests should check bounds, deterministic seed repeatability, center behavior, and distribution sanity rather than exact full sequences unless seed and algorithm are fixed.
