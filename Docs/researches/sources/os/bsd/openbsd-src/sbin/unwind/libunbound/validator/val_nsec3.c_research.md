# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.c

This file implements NSEC3 denial-of-existence proof logic for DNSSEC validation. It handles NSEC3 parsing, parameter filtering, hash calculation and caching, closest-encloser proofs, wildcard nonexistence, NODATA, NXDOMAIN, DS no-data, and combined NXDOMAIN-or-NODATA validation.

Core structures:
- `ce_response` stores closest-encloser proof state: closest encloser name, matching NSEC3, and next-closer covering NSEC3.
- `nsec3_filter` restricts candidate NSEC3 records to the relevant zone, class, known algorithm, and known flags.
- `nsec3_cached_hash` stores name hash outputs, base32 labels, and cache keys.
- `nsec3_cache_table` owns a regional rbtree cache for repeated hash lookups.

Parsing and filtering:
- `nsec3_get_params()`, `nsec3_get_nextowner()`, `nsec3_has_type()`, and `nsec3_has_optout()` parse individual NSEC3 RDATA fields with length checks.
- `filter_init()`, `filter_first()`, and `filter_next()` select usable NSEC3 RRs for the best matching zone.
- Unknown algorithms or unknown flags are ignored by the iterator.
- `param_set_same()` rejects mixed NSEC3 chains with mismatched algorithm, iteration count, or salt.

Hashing:
- `nsec3_get_hashed()` computes NSEC3 iterative hashes.
- `nsec3_hash_name()` caches computed hashes in an rbtree keyed by name plus NSEC3 parameters.
- `nsec3_hash_cmp()` compares cache keys using dname, algorithm, iteration count, and salt.
- `nsec3_hash_to_b32()` and `nsec3_get_nextowner_b32()` construct base32 owner names.

Proof mechanics:
- `find_matching_nsec3()` finds an NSEC3 whose owner matches a hashed name.
- `find_covering_nsec3()` finds an NSEC3 span covering a hashed name.
- `nsec3_covers()` implements normal and wraparound hash interval coverage.
- `nsec3_find_closest_encloser()` walks from qname toward zone apex until a matching NSEC3 is found.
- `nsec3_prove_closest_encloser()` verifies the closest-encloser candidate and next-closer coverage, rejecting DNAME and invalid delegation cases.

Public proof entry points:
- `nsec3_prove_nameerror()` proves NXDOMAIN by proving closest encloser, next closer nonexistence, and wildcard nonexistence.
- `nsec3_prove_nodata()` proves NODATA using matching NSEC3, wildcard NODATA, and opt-out cases.
- `nsec3_prove_wildcard()` proves positive wildcard applicability by covering the next closer.
- `nsec3_prove_nods()` verifies DS absence, including normal NODATA and opt-out DS NODATA.
- `nsec3_prove_nxornodata()` tries NXDOMAIN first, then NODATA while preserving the hash cache.

Security behavior:
- Uses `MAX_NSEC3_CALCULATIONS` to limit expensive hashing and returns `sec_status_unchecked` when proof should be suspended/retried.
- Treats all attempted hash calculations failing as bogus via `MAX_NSEC3_ERRORS`.
- Enforces validator-configured maximum NSEC3 iterations based on DNSKEY size; excessive iterations return insecure.
- Opt-out spans generally produce insecure results rather than secure AD-valid answers.
- DS proofs require NSEC3 RRsets to be cryptographically secure first via `list_is_secure()`.

Important dependencies:
- `val_secalgo.c` for NSEC3 SHA-1 hashing.
- `val_nsec.h` for NSEC/NSEC3 bitmap type checks.
- validator key entries for key size and key validity.
- regional allocator and scratch buffer for temporary proof state.

Research notes:
- The implementation is careful about malformed RDATA and mixed-chain proofs.
- The hash cache is central because several proof paths repeatedly hash qname, ancestors, next-closer names, and wildcard names.
- The code distinguishes bogus proof failure, insecure opt-out/delegation behavior, and unchecked computational deferral.
