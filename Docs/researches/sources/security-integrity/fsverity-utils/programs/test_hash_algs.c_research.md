# sources/security-integrity/fsverity-utils/programs/test_hash_algs.c

Purpose: This test program verifies public hash algorithm lookup and digest-size APIs.

Important APIs and functions: It calls `libfsverity_find_hash_alg_by_name()` and `libfsverity_get_digest_size()` for supported algorithms such as SHA-256 and SHA-512, plus unknown names/numbers.

Control flow and state: Tests are simple assertions over immutable algorithm metadata. There is no persistent state.

Dependencies and integration points: Protects CLI `--hash-alg` parsing, library parameter validation, and digest-size allocation behavior.

Risks and test signals: Risk is low but important: changing names, numbers, or digest sizes would break ABI and vectors. Signals are exact algorithm number and digest-size matches and zero results for unknown algorithms.
