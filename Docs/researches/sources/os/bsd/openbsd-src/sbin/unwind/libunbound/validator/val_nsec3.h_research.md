# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.h

This header defines the NSEC3 validator API and supporting cache structures. It documents NSEC3 and NSEC3PARAM wire layout and declares proof functions used by the DNSSEC validator.

Key constants:
- `NSEC3_OPTOUT` is the opt-out flag.
- `NSEC3_UNKNOWN_FLAGS` masks unsupported flags.
- `NSEC3_HASH_SHA1` is the supported NSEC3 hash algorithm.
- `MAX_NSEC3_CALCULATIONS` limits per-pass NSEC3 hash work.

Public proof API:
- `nsec3_prove_nameerror()` proves NXDOMAIN with closest-encloser, next-closer, and wildcard proofs.
- `nsec3_prove_nodata()` proves NOERROR/NODATA across normal, wildcard, ENT, and opt-in/opt-out DS cases.
- `nsec3_prove_wildcard()` proves a positive wildcard response was appropriate.
- `nsec3_prove_nods()` proves no DS or insecure opt-out DS absence.
- `nsec3_prove_nxornodata()` tries to prove either NXDOMAIN or NODATA and reports which proof succeeded.

Hash/cache API:
- `struct nsec3_cache_table` stores a regional rbtree pointer and its allocation region.
- `struct nsec3_cached_hash` records NSEC3 parameters, dname, raw hash, and base32 label.
- `nsec3_cache_table_init()` initializes the cache.
- `nsec3_hash_cmp()` is the rbtree comparator.
- `nsec3_hash_name()` returns cached or newly computed hashes.

Parsing helpers:
- `nsec3_get_nextowner_b32()` and `nsec3_hash_to_b32()` construct base32 owner names.
- `nsec3_get_params()` returns algorithm, iterations, and salt.
- `nsec3_get_hashed()` computes raw NSEC3 hashes.
- `nsec3_has_type()`, `nsec3_has_optout()`, and `nsec3_get_nextowner()` inspect individual NSEC3 RRs.
- `nsec3_covers()` tests whether an NSEC3 RR covers a hash.

Research notes:
- The header explicitly exposes some internal mechanics for unit testing.
- Return status semantics are important: secure, bogus, insecure, unchecked, and indeterminate carry different validator meanings.
- The cache structure stores pointers into regional allocation, so callers must reinitialize after region cleanup.
