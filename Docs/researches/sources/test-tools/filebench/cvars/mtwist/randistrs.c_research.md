## sources/test-tools/filebench/cvars/mtwist/randistrs.c

### Purpose
`randistrs.c` implements probability distributions on top of the mtwist PRNG. It provides state-based `rds_*` functions and default-generator `rd_*` wrappers for uniform integer/floating distributions, exponential, Erlang, Weibull, normal, lognormal, triangular, and empirical distributions.

### Important APIs, Types, And Functions
Uniform integer APIs are `rds_iuniform` and, when `INT64_MAX` exists, `rds_liuniform`. Floating uniform APIs are `rds_uniform` and `rds_luniform`. Transform-based distributions include `rds_exponential`, `rds_erlang`, `rds_weibull`, `rds_normal`, `rds_lognormal`, and `rds_triangular`, each with long-precision `l` variants. Empirical support is built around `rd_empirical_setup`, `rd_empirical_free`, `rds_int_empirical`, `rds_double_empirical`, and `rds_continuous_empirical`. The `rd_*` functions delegate to the same stateful implementations using `mt_default_state`.

### Control Flow
The integer-uniform functions use a fast double-scaling path for small ranges below `RD_UNIFORM_THRESHOLD`, then switch to rejection sampling with a computed bitmask for larger ranges to avoid unacceptable bias. Exponential, Erlang, Weibull, and normal distributions repeatedly draw until the random input avoids zero or invalid transform domains. Normal uses the polar form of Box-Muller and discards the second variate to stay reentrant. Empirical setup normalizes caller weights, divides entries into low/high stacks, builds alias-style cutoff/remap tables in O(n), then generation scales a uniform value by `n` and either returns the direct slot or its remap.

### State And Persistence
The file does not maintain persistent distribution state except in heap-allocated `rd_empirical_control` structures returned by `rd_empirical_setup`. Those controls own `cutoff`, `remap`, and `values` arrays and must be freed with `rd_empirical_free`. Random-generator state is external: either supplied `mt_state *` or `mt_default_state`.

### Dependencies And Integration Points
It depends on `mtwist.h`, `randistrs.h`, `math.h`, and `stdlib.h`. The C++ wrapper in `randistrs.h` directly calls these functions. The standalone test programs `rdtest.c` and `rdcctest.cc` exercise these APIs from the command line.

### Risks
Parameter validation is mostly left to callers. Invalid bounds such as `upper <= lower`, nonpositive means/scales, or invalid triangular mode can produce biased, nonsensical, or undefined math results. `rd_empirical_setup` copies `n_probs + 1` values when `values` is provided, so callers that pass only `n_probs` entries risk out-of-bounds reads. The code assigns `control->remap` twice before allocating `values`, leaking the first allocation. Empirical setup also divides by `prob_total`; all-zero weights would be invalid. `MT_CACHING` makes integer mask caching static and non-reentrant.

### Test Signals
Useful tests include deterministic output for fixed seeds, boundary checks for integer ranges, rejection-sampling behavior near large ranges, statistical smoke tests for each distribution, empirical alias-table coverage, and allocation-failure cleanup tests for `rd_empirical_setup`. Existing `rdtest` and `rdcctest` are generation harnesses but do not assert distribution quality.
