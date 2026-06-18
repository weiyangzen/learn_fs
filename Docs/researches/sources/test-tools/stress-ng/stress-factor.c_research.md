# sources/test-tools/stress-ng/stress-factor.c

Purpose: implements `factor`, a GMP-backed integer stressor that generates large composite integers and factors them by repeated division over prime candidates.

Important APIs/types/functions: option `factor-digits` bounds requested decimal digits from 8 to 100,000,000. `stress_factor()` uses GMP `mpz_t` values for the target, divisor, quotient, remainder, and temporary factors; key GMP calls include `mpz_mul`, `mpz_sizeinbase`, `mpz_sqrt`, `mpz_cdiv_qr`, and `mpz_nextprime`.

Control flow: after option parsing and GMP initialization, the stressor sync-starts. Each iteration builds a value by multiplying small odd non-multiple-of-three random chunks until the decimal digit target is reached. It then sets the divisor to 2, computes a square-root bound, repeatedly divides, records successful factors, advances to the next prime on nonzero remainder, and stops when the divisor exceeds the bound or the value reaches 1. It increments bogo operations and records timing.

State and persistence behavior: all state is in local GMP objects and scalar metric accumulators. There is no filesystem or shared state. GMP objects are cleared on exit.

Dependencies and integration points: requires `gmp.h` and libgmp; otherwise registers unimplemented. Integrates with stress-ng settings, maximize/minimize flags, random helpers, timing, bogo counters, metrics, and process-state reporting. Classifier is `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE`.

Risks: very large digit counts can consume substantial CPU and memory. The factor generator intentionally produces composites from small chunks, so it is a stress workload rather than a cryptographic factor benchmark. Stop checks inside both generation and factoring are required to avoid long uninterruptible operations.

Test signals: build with and without GMP, run minimum/default/moderate `--factor-digits`, confirm metrics for average factors, milliseconds per factorization, and largest digits, and check graceful stop during long factorizations.
