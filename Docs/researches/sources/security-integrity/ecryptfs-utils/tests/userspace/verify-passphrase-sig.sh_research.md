## sources/security-integrity/ecryptfs-utils/tests/userspace/verify-passphrase-sig.sh

Purpose: Regression script for libecryptfs `generate_passphrase_sig()`. It runs a compiled C helper against three fixed passphrase/salt pairs and expected signature/FEKEK outputs derived from ecryptfs-utils version 30.

Important APIs and functions: variables `pass`, `salt`, `expected_sig`, `expected_fekek`, calls `${test_script_dir}/verify-passphrase-sig/test`. Control flow executes the helper for each vector, exits immediately on the first failure, and returns the final helper status.

State and persistence: No filesystem/keyring state; all checks are deterministic in process memory. Dependencies are bash and the linked C helper/libecryptfs. Integration is `make check` through `userspace/Makefile.am` and optional `run_tests.sh -U`. Risk is intentional compatibility lock-in: any cryptographic derivation change, even deliberate, must update vectors and compatibility expectations.
