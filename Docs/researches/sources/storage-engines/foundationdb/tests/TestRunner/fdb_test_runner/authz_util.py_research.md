# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/authz_util.py

- **Purpose:** JWT/JWK helper utilities for temporary-cluster authorization tests. It creates EC/RSA keys, public key sets, and short-lived tenant authorization claims.
- **Source facts:** 67 lines, 1785 bytes, executable=False.
- **Important APIs/types/functions:** Imports: .test_util.random_alphanum_string, authlib.jose.JsonWebKey, authlib.jose.KeySet, authlib.jose.jwt, base64, json, time, typing.List, typing.Union. Classes: none. Top-level functions: to_str, private_key_gen, public_keyset_from_keys, alg_from_kty, token_gen, token_claim_1h. Methods: none. Constants: none. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: .test_util.random_alphanum_string, authlib.jose.JsonWebKey, authlib.jose.KeySet, authlib.jose.jwt, base64, json, time, typing.List, typing.Union; authlib.jose supplies JWK/JWT primitives.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
