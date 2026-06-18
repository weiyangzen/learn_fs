# sources/test-tools/fio/lib/gauss.h

Purpose: declares Gaussian distribution state and API for fio random offset generation.

Important APIs/types: `struct gauss_state` stores `nranges`, deviance, random offset, and an embedded `frand_state`; `gauss_init` seeds/configures it; `gauss_next` returns the next bounded value.

Control flow/state: callers keep one state per distribution stream and repeatedly call `gauss_next`. State mutation happens through the embedded RNG.

Dependencies/integration: includes `rand.h` and integer types. Used by workload option code that selects non-uniform random distributions.

Risks/test signals: callers must initialize before use and treat output as deterministic for a given seed/config. Tests should cover range boundaries and center/deviation options.
