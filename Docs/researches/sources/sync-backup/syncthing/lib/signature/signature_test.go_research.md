# sources/sync-backup/syncthing/lib/signature/signature_test.go

Purpose: verifies key generation, signing, and signature verification against embedded fixture material.

Important tests: `TestGenerateKeys` checks generated PEM blocks contain private and public key labels. `TestSign` signs a known string with an embedded private key and verifies the returned PEM is labeled `SIGNATURE`. `TestVerify` verifies a precomputed signature for the expected string and confirms changed data is rejected.

State and persistence: uses static PEM private/public keys and signature bytes in memory only.

Dependencies and integration: exercises the public `signature` package from an external test package, matching real caller usage.

Risks and signals: good regression coverage for the public API and fixture compatibility, but no tests for invalid private keys, invalid public keys, malformed signatures, reader errors, or alternate curves.
