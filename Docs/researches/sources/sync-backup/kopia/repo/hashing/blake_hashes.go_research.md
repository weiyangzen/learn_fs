# sources/sync-backup/kopia/repo/hashing/blake_hashes.go

Purpose: registers keyed BLAKE2S and BLAKE2B hash variants used by repository content IDs.

Important APIs/types/functions: package `init`, `truncatedKeyedHashFuncFactory`, `blake2s.New128`, `blake2s.New256`, and `blake2b.New256`.

Control flow: initialization registers four algorithm names: `BLAKE2S-128`, `BLAKE2S-256`, `BLAKE2B-256-128`, and `BLAKE2B-256`, each with the intended truncation length.

State/persistence behavior: algorithm names are stored in repository content format; the default elsewhere is `BLAKE2B-256-128`.

Dependencies/integration: depends on `golang.org/x/crypto/blake2b` and `blake2s`, plus the registry in `hashing.go`.

Risks/test signals: registration order is not externally meaningful because supported algorithms are sorted. Tests cover round-trip stability and differing data outputs but not fixed golden digests.
