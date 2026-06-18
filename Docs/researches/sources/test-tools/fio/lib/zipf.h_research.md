# sources/test-tools/fio/lib/zipf.h

Purpose: declares shared state and APIs for Zipf/Pareto random distributions.

Important APIs/types: `struct zipf_state` with range count, theta, zeta values, Pareto exponent, embedded RNG, random offset, and hash-disable bool; `zipf_init`, `zipf_next`, `pareto_init`, `pareto_next`, and `zipf_disable_hash`.

Control flow/state: callers initialize one state per stream and repeatedly call next functions. The same struct supports both Zipf and Pareto depending on initialization.

Dependencies/integration: includes `rand.h` and bool types. Consumed by fio workload randomization code.

Risks/test signals: callers must not mix next functions with the wrong initialization without understanding shared fields. Tests should verify API-level bounds and reproducible sequences.
