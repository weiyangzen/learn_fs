# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hashutil.py

Purpose: tests Tahoe's domain-separated hashing utilities and cryptographic key-derivation helpers. It locks down byte return types, digest lengths, tagged hash compatibility, convergence hashing, timing-safe comparison, storage index derivation, mutable file hashes, lease secret hashes, HMAC, and server permutation hashes.

Important APIs and types are concentrated in `HashUtilTests`. Tested functions include `random_key`, `tagged_hash`, `tagged_hasher`, `tagged_pair_hash`, `convergence_hash`, `convergence_hasher`, `_convergence_hasher_tag`, `storage_index_hash`, all immutable block/plaintext/crypttext/segment hash helpers, mutable SSK key/hash helpers, lease renewal/cancel secret hashes, `hmac`, `permute_server_hash`, and `timing_safe_compare`.

Control flow compares direct one-shot helpers to incremental hasher objects, verifies truncated hash sizes, checks known base32 answers for several tagged inputs, derives convergence keys from encoding parameters and a secret, and validates `_convergence_hasher_tag` format and parameter bounds. `_testknown` centralizes compatibility assertions by base32-encoding returned bytes. The known-answer block covers empty inputs and representative secret/key/storage-index values across immutable, mutable, lease, and peer-selection domains.

State and persistence are absent aside from random bytes returned by `random_key`. The critical state behavior is hasher object idempotence: calling `.digest()` twice yields the same bytes after updates, and domain parameters are encoded into tags deterministically.

Dependencies include Twisted Trial, `allmydata.util.hashutil`, and Tahoe base32 conversion. Integration points are almost every Tahoe capability and storage workflow: CHK convergence keys, storage indexes, share/block/segment hash trees, mutable SSK caps, lease secrets, write enablers, and deterministic server ordering.

Risks covered include accidental domain-separation tag changes, digest truncation changes, return type regressions to text, accepting invalid convergence parameters, non-constant-time compare semantics for equal/unequal lengths, known-answer drift that would break old caps or stored shares, and server permutation changes that alter share placement. Residual risk is that cryptographic strength is not proven by these tests; they are API and compatibility checks.

Test signals include exact digest lengths, exact base32 known answers, raised `ValueError` for bad k/n bounds, `AssertionError` when applicable input types are wrong through helper calls, true/false timing compare results, and equality between one-shot and streaming hasher outputs.
