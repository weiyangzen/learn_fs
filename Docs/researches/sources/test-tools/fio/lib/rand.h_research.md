# sources/test-tools/fio/lib/rand.h

Purpose: declares fio random state types and inline random number generation helpers.

Important APIs/types: `struct taus88_state`, `taus258_state`, `frand_state`, max constants, `rand_max`, copy helpers, inline `__rand32`, `__rand64`, `__rand`, `__rand_0_1`, bounded `rand32_upto`/`rand64_upto`, `rand_between`, `__get_next_seed`, and external initialization/fill functions.

Control flow/state: callers choose 32- or 64-bit mode in `frand_state`; every random draw mutates embedded Tausworthe state. Bounded helpers scale random integers through double arithmetic.

Dependencies/integration: includes fio bool and assertions. Used by distributions, data fill, benchmarks, and workload selection.

Risks/test signals: bounded generation can have rounding bias, especially for large 64-bit ranges. Tests should cover repeatability, state copying, boundary values, and 32/64-bit mode assertions.
