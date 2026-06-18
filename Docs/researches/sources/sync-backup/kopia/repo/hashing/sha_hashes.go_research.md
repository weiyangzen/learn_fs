# sources/sync-backup/kopia/repo/hashing/sha_hashes.go

Purpose: registers HMAC-based SHA-2 and SHA-3 hashing algorithms for content IDs.

Important APIs/types/functions: package `init`, `truncatedHMACHashFuncFactory`, `sha256.New`, `sha256.New224`, `sha3.New224`, and `sha3.New256`.

Control flow: initialization registers `HMAC-SHA256`, `HMAC-SHA256-128`, `HMAC-SHA224`, `HMAC-SHA3-224`, and `HMAC-SHA3-256` with appropriate output lengths.

State/persistence behavior: the selected HMAC algorithm and secret are part of repository content format. Hash output length affects content ID size and compatibility.

Dependencies/integration: uses standard crypto packages and the hashing registry.

Risks/test signals: HMAC secret omission or algorithm-name drift affects repository compatibility. The shared hashing test covers registration and deterministic behavior.
