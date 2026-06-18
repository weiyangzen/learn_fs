# sources/test-tools/stress-ng/core-prime.h

Purpose: declares 64-bit prime helpers.

Important APIs/types: `stress_prime64_check`, `stress_prime64_next_get`, and `stress_prime64_get`.

Control flow: no header runtime flow; attributes mark checking and warn on ignored results.

State/persistence: no header state; `stress_prime64_next_get` has implementation-static state.

Dependencies/integration: includes `stress-ng.h` for integer types and attributes. Used by code needing stride values not sharing factors with a target.

Risks: callers expecting deterministic `stress_prime64_next_get` must account for its static rolling state.

Test signals: compile users and verify ignored-result warnings where supported.
