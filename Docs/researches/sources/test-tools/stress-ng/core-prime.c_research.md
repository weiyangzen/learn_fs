# sources/test-tools/stress-ng/core-prime.c

Purpose: provides simple 64-bit prime testing and prime selection helpers used for stride values.

Important APIs/functions: `stress_prime64_check`, `stress_prime64_next_get`, and `stress_prime64_get`.

Control flow: primality handles small values, rejects divisible-by-2/3 cases, then tests `6k +/- 1` factors up to `sqrt(n)+1`. Prime getters search up to 2000 odd candidates above `n` for a prime that does not divide `n`; `next_get` uses a static rolling candidate while `get` is stateless and falls back to the largest 64-bit prime.

State/persistence: `stress_prime64_next_get` keeps file-static `p`; no durable state.

Dependencies/integration: `stress_continue_flag`, `shim_sqrt`, and common branch/attribute macros.

Risks: static `p` is not thread-safe; search can stop early during termination; double sqrt can be imprecise near very large values though loop is conservative; fallback behavior differs between variants.

Test signals: known prime/composite vectors, small values, values near `UINT64_MAX`, repeated next-call uniqueness, stop-flag behavior, and concurrent callers.
