# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.c

This file provides high-level validator utility logic around response classification, signer discovery, RRset validation cache updates, DS/DNSKEY trust-chain validation, wildcard/CNAME/DNAME handling, message cleanup, and cached DS lookup.

Response classification:
- `val_classify_response()` classifies replies as name error, NODATA, referral, positive, CNAME, CNAME-no-answer, ANY, or unknown.
- It handles non-recursive referrals, root referral form, CNAME chains ending in NXDOMAIN, DNAME query special cases, and ANY responses.
- `val_classification_to_string()` formats classifications for logging.

Signer discovery:
- `rrsig_get_signer()` parses signer names from RRSIG RDATA.
- `val_find_rrset_signer()` returns the first RRSIG signer.
- `val_find_best_signer()` chooses the closest signer for CNAME-no-answer authority proofs.
- `cname_under_previous_dname()` detects synthesized CNAMEs caused by previous DNAMEs.
- `val_find_signer()` selects appropriate signer names depending on response subtype.

RRset verification:
- `val_verify_rrset()` checks cached security status, invokes `dnskeyset_verify_rrset()`, updates RRset security/trust, adjusts bogus TTLs, increments bogus counters, and stores status in the RRset cache.
- `val_verify_rrset_entry()` creates a temporary DNSKEY RRset view from a key entry and verifies an RRset against it.

DS/DNSKEY validation:
- `verify_dnskeys_with_ds_rr()` matches one DS against candidate DNSKEYs by algorithm, keytag, digest, key size, and DNSKEY self-signature.
- `val_favorite_ds_algo()` chooses the highest-numbered supported DS digest algorithm.
- `val_verify_DNSKEY_with_DS()` validates DNSKEY RRsets through DS RRsets, including downgrade protection with `algo_needs`.
- `val_verify_new_DNSKEYs()` creates good, null, or bad key entries from DS-based validation results.
- `val_verify_DNSKEY_with_TA()` validates DNSKEY RRsets against trust-anchor DS and/or DNSKEY RRsets.
- `val_verify_new_DNSKEYs_with_ta()` creates key entries from trust-anchor validation results.
- `val_dsset_isusable()` checks whether a DS set has at least one supported digest/key algorithm pair.

Wildcard and CNAME/DNAME handling:
- `val_rrset_wildcard()` detects whether an RRset was wildcard synthesized by comparing RRSIG label counts.
- `val_chase_cname()` advances a query-info chase through matching CNAME records.
- `derive_cname_from_dname()` constructs the expected CNAME target from a DNAME owner and target.

Reply construction and cleanup:
- `val_fill_reply()` builds a chase reply containing RRsets matching a name or signer, with special handling for DNAME-generated unsigned CNAMEs.
- `val_reply_remove_auth()` removes one authority-section RRset.
- `val_check_nonsecure()` marks a message bogus if required authority data is not secure, but may remove nonessential insecure NS/additional data for lenient minimal responses.
- `val_mark_indeterminate()` marks unchecked RRsets indeterminate when no trust anchor applies.
- `val_mark_insecure()` marks unchecked RRsets insecure below an insecure key name.
- `val_next_unchecked()` finds the next unchecked RRset after a given index.

Other helpers:
- `val_blacklist()` merges or prepends origin socket lists into a validator blacklist.
- `val_has_signed_nsecs()` checks whether authority NSEC/NSEC3 records have signatures and supplies a failure reason.
- `val_find_DS()` looks for DS data in the RRset cache first, then negative cache, returning an internal DNS message.

Security behavior:
- DS matching limits repeated digest mismatches per DS with `MAX_DS_MATCH_FAILURES`.
- Unsupported DS/DNSKEY algorithms can lead to insecure status when no useful supported chain exists.
- Bogus RRsets have TTLs clamped to validator bogus TTL and are counted under lock.
- Trust-anchor mismatch by owner name is immediately bogus.
- Additional-section cleanup can remove unsigned data without invalidating the whole message when configured.

Research notes:
- This file ties together `val_sigcrypt`, key-entry creation, anchors, caches, and negative proof lookup.
- It is high-level validation glue rather than low-level crypto or NSEC proof code.
- The response classification and signer-finding paths are central for deciding which key name to fetch and which RRsets to validate next.
