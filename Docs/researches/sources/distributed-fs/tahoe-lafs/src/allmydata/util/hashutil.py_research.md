# sources/distributed-fs/tahoe-lafs/src/allmydata/util/hashutil.py

## Purpose

This module defines Tahoe-LAFS cryptographic hash domain separation, key derivation, lease secret derivation, storage index derivation, convergence hashing, mutable-cap derivations, and timing-safe comparison. The header warns that almost any change can invalidate existing URIs and stored data.

## APIs and control flow

`_SHA256d_Hasher` implements double SHA-256 with optional truncation and cached final digest. `tagged_hasher()`, `tagged_hash()`, and `tagged_pair_hash()` netstring tags/inputs for domain separation. Named helpers derive immutable storage indexes, block hashes, URI-extension hashes, plaintext/ciphertext segment hashes, convergence keys, random keys, renewal/cancel secrets, bucket secrets, mutable read/write/enabler keys, dirnode child cap keys/salts, backup DB hashes, and server permutation hashes.

`_convergence_hasher_tag()` validates `k`, `n`, zfec limits, and convergence-secret type before building the tag. `hmac()` implements a local SHA-256 construction over tag/data. `timing_safe_compare()` hashes both inputs under a random tag and compares digests.

## State, dependencies, risks, and tests

State is constants and hasher objects. Persistent compatibility is extremely high: tags, truncation lengths, netstring framing, and hash algorithms are part of stored capability and share semantics. Dependencies are `hashlib`, `os.urandom`, and local `netstring`.

Risks include changing any tag string, accepting invalid erasure parameters, relying on assertions for peer id lengths, nonstandard HMAC construction, and SHA-1 in server permutation for historical behavior. Test signals should include golden vectors for every derivation, convergence parameter validation, URI compatibility, lease secret derivation, mutable cap round-trips, timing compare equality/inequality, and old-data fixtures.
